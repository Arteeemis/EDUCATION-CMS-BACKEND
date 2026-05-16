"""Админ-регистрация пунктов меню (только для администратора)."""

from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin

from users.admin_mixins import AdminOnlyMixin

from .models import HeaderLink


@admin.register(HeaderLink)
class HeaderLinkAdmin(AdminOnlyMixin, SortableAdminMixin, admin.ModelAdmin):
    list_display = ("title", "block", "target_page", "external_url", "is_visible", "position")
    list_filter = ("block", "is_visible")
    search_fields = ("title", "external_url")
    autocomplete_fields = ("block", "target_page")
    fieldsets = (
        (None, {"fields": ("block", "title", "is_visible")}),
        (
            "Куда ведёт ссылка",
            {
                "description": "Заполните либо внутреннюю страницу, либо внешний URL",
                "fields": ("target_page", "external_url"),
            },
        ),
    )