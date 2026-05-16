"""Админ-регистрация модели пользователя (только для администратора)."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .admin_mixins import AdminOnlyMixin
from .models import User


@admin.register(User)
class UserAdmin(AdminOnlyMixin, DjangoUserAdmin):
    """Расширенная админка пользователя с полем роли."""

    list_display = ("username", "email", "role", "is_active", "is_staff", "created_at")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-created_at",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Роль в CMS", {"fields": ("role",)}),
        ("Служебные даты", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "last_login", "date_joined")

    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Роль в CMS", {"fields": ("role", "email")}),
    )
