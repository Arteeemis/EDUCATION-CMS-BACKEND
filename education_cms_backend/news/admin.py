"""
Админ-регистрация публикаций.

Логика прав:
- Администратор видит и редактирует все публикации, может выбрать любую ленту
  и любого автора.
- Редактор видит и редактирует только публикации в своих лентах (где он
  назначен редактором). В форме создания поста доступны только его ленты.
  Автор публикации автоматически устанавливается равным редактору.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "news_feed",
        "author",
        "urgent_badge",
        "image_preview",
        "published_at",
        "created_at",
    )
    list_filter = ("is_urgent", "news_feed")
    search_fields = ("title", "content", "tags")
    autocomplete_fields = ("news_feed",)

    fieldsets = (
        (None, {"fields": ("news_feed", "title", "content")}),
        ("Медиа и метаданные", {"fields": ("image", "tags")}),
        ("Публикация", {"fields": ("is_urgent", "published_at")}),
        (
            "Служебные даты",
            {"classes": ("collapse",), "fields": ("author", "created_at", "updated_at")},
        ),
    )
    readonly_fields = ("author", "created_at", "updated_at")

    # ---------- Бейджи ----------
    @admin.display(description="Срочно", ordering="is_urgent")
    def urgent_badge(self, obj):
        if obj.is_urgent:
            return format_html(
                '<span style="background:#dc2626;color:#fff;padding:2px 8px;'
                'border-radius:10px;font-size:11px;">СРОЧНО</span>'
            )
        return ""

    @admin.display(description="Превью")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:30px;border-radius:4px;" />',
                obj.image.url,
            )
        return "—"

    # ---------- Доступ к разделу ----------
    def has_module_permission(self, request):
        """Раздел виден администратору и редактору."""
        if not request.user.is_authenticated:
            return False
        return request.user.is_admin_role or request.user.is_editor_role

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        """Редактор может добавлять только если у него есть назначенные ленты."""
        if not request.user.is_authenticated:
            return False
        if request.user.is_admin_role:
            return True
        if request.user.is_editor_role:
            return request.user.news_feeds.exists()
        return False

    def has_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            return False
        if request.user.is_admin_role:
            return True
        if request.user.is_editor_role:
            # На уровне списка — да; объектные проверки делает get_queryset
            if obj is None:
                return True
            return obj.news_feed.editors.filter(pk=request.user.pk).exists()
        return False

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    # ---------- Фильтрация queryset ----------
    def get_queryset(self, request):
        """Редактор видит только посты в своих лентах."""
        qs = super().get_queryset(request).select_related("news_feed", "author")
        if request.user.is_authenticated and request.user.is_editor_role:
            return qs.filter(news_feed__editors=request.user)
        return qs

    # ---------- Ограничение выбора в FK ----------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Редактор в выпадашке news_feed видит только свои ленты."""
        if (
            db_field.name == "news_feed"
            and request.user.is_authenticated
            and request.user.is_editor_role
        ):
            kwargs["queryset"] = request.user.news_feeds.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # ---------- Автоматическое заполнение автора ----------
    def save_model(self, request, obj, form, change):
        """Автор всегда = текущий пользователь (на создании)."""
        if not change or not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)