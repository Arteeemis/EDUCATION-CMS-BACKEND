"""Админ-регистрация модели пользователя (только для администратора)."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from .admin_mixins import AdminOnlyMixin
from .forms import AdminPasswordChangeForm
from .models import User

# В нашей системе используется собственная ролевая модель через поле role,
# поэтому встроенные Django Groups для разграничения прав не нужны.
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAdmin(AdminOnlyMixin, DjangoUserAdmin):
    """Расширенная админка пользователя с полем роли.

    Особенности:
    - Скрыта техническая информация о хеше пароля — вместо неё кнопка «Сбросить пароль»
    - Скрыто поле «Аутентификация по паролю» (usable_password) в форме смены
    - Удаление пользователей через UI запрещено — только деактивация
    - Скрыты Groups и User permissions (используется наша ролевая модель)
    - Скрыт is_superuser — управляется только через CLI
    """

    change_password_form = AdminPasswordChangeForm

    list_display = ("username", "email", "role", "is_active", "is_staff", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("username", "password_reset_button")}),
        ("Личная информация", {"fields": ("first_name", "last_name", "email")}),
        ("Роль в CMS", {"fields": ("role",)}),
        (
            "Технический доступ",
            {
                "classes": ("collapse",),
                "fields": ("is_active", "is_staff"),
                "description": (
                    "Технические флаги Django. В типичном случае их менять не нужно — "
                    "роль в CMS определяется полем «Роль» выше. "
                    "Для деактивации учётной записи используйте флаг «Активный» — это "
                    "сохраняет целостность связанных данных (авторство публикаций и др.). "
                    "Флаг суперпользователя управляется только через CLI."
                ),
            },
        ),
        (
            "Служебные даты",
            {
                "classes": ("collapse",),
                "fields": ("last_login", "date_joined"),
            },
        ),
    )

    readonly_fields = ("last_login", "date_joined", "password_reset_button")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "role", "password1", "password2"),
            },
        ),
    )

    @admin.display(description="Пароль")
    def password_reset_button(self, obj):
        """Заменяет стандартное отображение поля password.

        Вместо хеша алгоритма и параметров показывает только кнопку
        «Сбросить пароль» со ссылкой на форму смены пароля.
        """
        if not obj or not obj.pk:
            return "—"
        return format_html(
            '<a href="../password/" class="button" '
            'style="background:#1e3a8a;color:#fff;padding:8px 16px;'
            "border-radius:6px;text-decoration:none;font-weight:500;"
            'display:inline-block;">Сбросить пароль</a>'
        )

    def has_delete_permission(self, request, obj=None):
        """Удаление пользователей запрещено — используется деактивация."""
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
