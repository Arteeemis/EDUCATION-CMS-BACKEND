"""
Админ-регистрация моделей блоков.

Доступ:
- HTML-блок, FAQ-блок, Меню (шапка), Контакты (подвал) — только администратор.
- Новостная лента — администратор полный доступ; редактор видит только свои
  ленты в режиме только для чтения (для понимания контекста публикаций).
"""

from django.contrib import admin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from users.admin_mixins import AdminOnlyMixin, AdminWriteEditorReadMixin

from .models import (
    HtmlBlock,
    FaqBlock,
    Question,
    NewsFeed,
    HeaderLinksBlock,
    FooterContactsBlock,
)


# ---------------------------------------------------------------------------
# HTML-блок (только администратор)
# ---------------------------------------------------------------------------
@admin.register(HtmlBlock)
class HtmlBlockAdmin(AdminOnlyMixin, admin.ModelAdmin):
    list_display = ("id", "admin_label", "created_at", "updated_at")
    search_fields = ("admin_label", "html_content")
    fields = ("admin_label", "html_content", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


# ---------------------------------------------------------------------------
# FAQ-блок (только администратор)
# ---------------------------------------------------------------------------
class QuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Question
    extra = 1
    fields = ("question", "answer")


@admin.register(FaqBlock)
class FaqBlockAdmin(AdminOnlyMixin, SortableAdminBase, admin.ModelAdmin):
    list_display = ("id", "title", "admin_label", "created_at")
    search_fields = ("title", "admin_label")
    fields = ("admin_label", "title", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = [QuestionInline]


# ---------------------------------------------------------------------------
# Новостная лента — администратор пишет, редактор читает свои ленты
# ---------------------------------------------------------------------------
@admin.register(NewsFeed)
class NewsFeedAdmin(AdminWriteEditorReadMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "admin_label",
        "editors_list",
        "post_count",
        "created_at",
    )
    search_fields = ("title", "admin_label")
    filter_horizontal = ("editors",)
    fieldsets = (
        (None, {"fields": ("admin_label", "title")}),
        ("Доступ", {"fields": ("editors",)}),
        (
            "Служебные даты",
            {"classes": ("collapse",), "fields": ("created_at", "updated_at")},
        ),
    )
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Кол-во публикаций")
    def post_count(self, obj):
        return obj.posts.count()

    @admin.display(description="Редакторы")
    def editors_list(self, obj):
        usernames = list(obj.editors.values_list("username", flat=True))
        return ", ".join(usernames) if usernames else "—"

    def get_queryset(self, request):
        """Редактор видит только те ленты, где он назначен редактором."""
        qs = super().get_queryset(request)
        if request.user.is_authenticated and request.user.is_editor_role:
            return qs.filter(editors=request.user)
        return qs

    def get_readonly_fields(self, request, obj=None):
        """Для редактора все поля только для чтения."""
        if request.user.is_authenticated and request.user.is_editor_role:
            return ("admin_label", "title", "editors", "created_at", "updated_at")
        return super().get_readonly_fields(request, obj)


# ---------------------------------------------------------------------------
# Блок-меню (только администратор)
# ---------------------------------------------------------------------------
@admin.register(HeaderLinksBlock)
class HeaderLinksBlockAdmin(AdminOnlyMixin, admin.ModelAdmin):
    list_display = ("id", "admin_label", "link_count", "created_at")
    search_fields = ("admin_label",)
    fields = ("admin_label", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Кол-во ссылок")
    def link_count(self, obj):
        return obj.links.count()


# ---------------------------------------------------------------------------
# Блок «Контакты в подвале» (только администратор)
# ---------------------------------------------------------------------------
@admin.register(FooterContactsBlock)
class FooterContactsBlockAdmin(AdminOnlyMixin, admin.ModelAdmin):
    list_display = ("id", "admin_label", "address", "phone", "email")
    search_fields = ("admin_label", "address", "phone", "email")
    fieldsets = (
        (None, {"fields": ("admin_label",)}),
        ("Контактные данные", {"fields": ("address", "phone", "email")}),
        (
            "Режим работы",
            {
                "fields": (
                    ("open_date", "close_date"),
                    ("open_time", "close_time"),
                    "weekends",
                )
            },
        ),
        (
            "Социальные сети",
            {"fields": ("vk_url", "tg_url", "max_url")},
        ),
        (
            "Служебные даты",
            {"classes": ("collapse",), "fields": ("created_at", "updated_at")},
        ),
    )
    readonly_fields = ("created_at", "updated_at")
