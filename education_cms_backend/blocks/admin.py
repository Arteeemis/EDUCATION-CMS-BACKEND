"""
Админ-регистрация моделей блоков.

Доступ:
- HTML-блок, FAQ-блок, Меню (шапка), Контакты (подвал) — только администратор.
- Новостная лента — администратор полный доступ; редактор видит только свои
  ленты в режиме только для чтения (для понимания контекста публикаций).
"""

from django.contrib import admin, messages
from django.utils.safestring import mark_safe
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
        "post_count_display",
        "created_at",
    )
    search_fields = ("title", "admin_label")
    filter_horizontal = ("editors",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Кол-во публикаций")
    def post_count_display(self, obj):
        return obj.posts.count()

    @admin.display(description="Редакторы")
    def editors_list(self, obj):
        usernames = list(obj.editors.values_list("username", flat=True))
        return ", ".join(usernames) if usernames else "—"

    @staticmethod
    def _posts_word(count):
        """Правильное склонение слова «публикация» в зависимости от числа."""
        if count == 1:
            return "публикация"
        if 2 <= count <= 4:
            return "публикации"
        return "публикаций"

    def get_fieldsets(self, request, obj=None):
        """При наличии постов добавляем жёлтую плашку предупреждения."""
        base_fieldsets = [
            (None, {"fields": ("admin_label", "title")}),
            ("Доступ", {"fields": ("editors",)}),
            (
                "Служебные даты",
                {"classes": ("collapse",), "fields": ("created_at", "updated_at")},
            ),
        ]

        if obj is not None and obj.pk:
            post_count = obj.posts.count()
            if post_count > 0:
                warning_html = (
                    '<div style="background:#fef3c7;border-left:4px solid #f59e0b;'
                    "padding:12px 16px;border-radius:6px;color:#854d0e;font-size:13px;"
                    'margin:0;">'
                    "<b>Внимание:</b> при удалении этой ленты будут "
                    "<b>безвозвратно удалены {count} {word}</b>, связанных с ней. "
                    "Если требуется временно скрыть ленту — используйте флаг "
                    "«Виден на сайте» в размещении блока на странице."
                    "</div>"
                ).format(count=post_count, word=self._posts_word(post_count))

                base_fieldsets.append(
                    (
                        None,
                        {
                            "fields": (),
                            "description": mark_safe(warning_html),
                        },
                    )
                )
        return base_fieldsets

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_authenticated and request.user.is_editor_role:
            return qs.filter(editors=request.user)
        return qs

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_authenticated and request.user.is_editor_role:
            return ("admin_label", "title", "editors", "created_at", "updated_at")
        return super().get_readonly_fields(request, obj)

    def delete_model(self, request, obj):
        post_count = obj.posts.count()
        super().delete_model(request, obj)
        if post_count > 0:
            messages.warning(
                request,
                f"Вместе с лентой удалено публикаций: {post_count}.",
            )

    def delete_queryset(self, request, queryset):
        total_posts = sum(feed.posts.count() for feed in queryset)
        super().delete_queryset(request, queryset)
        if total_posts > 0:
            messages.warning(
                request,
                f"Вместе с лентами удалено публикаций: {total_posts}.",
            )


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
