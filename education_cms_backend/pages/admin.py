"""
Админ-регистрация моделей страниц.

PageAdmin реализует визуальный конструктор: на форме редактирования
страницы виден список блоков, размещённых на ней, с drag-and-drop
сортировкой и удобным выпадающим списком для выбора блока.

Доступ ограничен ролью администратора.
"""

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from adminsortable2.admin import SortableTabularInline, SortableAdminBase

from blocks.models import Block

from .models import Page, PageBlock


# ---------------------------------------------------------------------------
# Кастомный ModelChoiceField для блоков —
# показывает понятное название с типом блока вместо ID
# ---------------------------------------------------------------------------
class BlockChoiceField(forms.ModelChoiceField):
    """Выпадающий список блоков с подписями «[Тип] Название»."""

    def label_from_instance(self, obj):
        # У полиморфной модели Block.objects.all() возвращает уже типизированные
        # инстансы (благодаря django-polymorphic), поэтому _meta.verbose_name
        # даёт корректный тип конкретного дочернего класса.
        real = obj.get_real_instance() if hasattr(obj, "get_real_instance") else obj
        type_name = real._meta.verbose_name
        label = real.admin_label or getattr(real, "title", "") or f"Блок #{real.pk}"
        return f"[{type_name}] {label}"


# ---------------------------------------------------------------------------
# Inline размещений блоков на странице
# ---------------------------------------------------------------------------
class PageBlockInline(SortableTabularInline):
    """Inline-конструктор блоков на странице.

    Администратор выбирает блок из выпадающего списка с понятными подписями.
    Порядок задаётся drag-and-drop.
    """

    model = PageBlock
    extra = 1
    fields = ("block", "block_type", "is_visible")
    readonly_fields = ("block_type",)

    verbose_name = "Блок"
    verbose_name_plural = "Размещённые блоки страницы"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Подмена виджета для поля block — кастомный ModelChoiceField."""
        if db_field.name == "block":
            kwargs["form_class"] = BlockChoiceField
            kwargs["queryset"] = Block.objects.all().order_by("-created_at")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description="Тип блока")
    def block_type(self, obj):
        if not obj.block_id:
            return "—"
        try:
            instance = obj.block.get_real_instance()
            return instance._meta.verbose_name
        except Exception:
            return obj.block.type


# ---------------------------------------------------------------------------
# Страница
# ---------------------------------------------------------------------------
@admin.register(Page)
class PageAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ("title", "slug", "status_badge", "blocks_count", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "status")}),
        ("Служебные даты", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    inlines = [PageBlockInline]

    @admin.display(description="Статус", ordering="status")
    def status_badge(self, obj):
        color = "#1e3a8a" if obj.is_published else "#94a3b8"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:10px;font-size:11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description="Блоков")
    def blocks_count(self, obj):
        return obj.page_blocks.count()

    # ---------- Доступ только для администратора ----------
    def has_module_permission(self, request):
        if not request.user.is_authenticated:
            return False
        return request.user.is_admin_role

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)
