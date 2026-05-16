"""
Админ-регистрация моделей страниц.

PageAdmin реализует визуальный конструктор: на форме редактирования
страницы виден список блоков, размещённых на ней, с drag-and-drop
сортировкой и возможностью добавлять/удалять блоки.

Доступ ограничен ролью администратора (редакторы не работают со страницами).
"""

from django.contrib import admin
from django.utils.html import format_html
from adminsortable2.admin import SortableTabularInline, SortableAdminBase

from .models import Page, PageBlock


# ---------------------------------------------------------------------------
# Inline размещений блоков на странице
# ---------------------------------------------------------------------------
class PageBlockInline(SortableTabularInline):
    """Inline-конструктор блоков на странице.

    Администратор выбирает существующий блок из выпадающего списка
    и располагает его на странице. Порядок задаётся drag-and-drop.
    """

    model = PageBlock
    extra = 1
    fields = ("block", "block_type", "is_visible")
    readonly_fields = ("block_type",)
    raw_id_fields = ("block",)

    verbose_name = "Блок"
    verbose_name_plural = "Размещённые блоки страницы"

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
