"""
Кастомные формы для админки пользователя.

Скрываем поле usable_password, добавленное в Django 5.1+.
"""

from django.contrib.auth.forms import (
    AdminPasswordChangeForm as DjangoAdminPasswordChangeForm,
)

from .models import User


class AdminPasswordChangeForm(DjangoAdminPasswordChangeForm):
    """Форма смены пароля без поля и кнопки usable_password."""

    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "usable_password" in self.fields:
            del self.fields["usable_password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
