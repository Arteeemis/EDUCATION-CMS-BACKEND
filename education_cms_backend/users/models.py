"""
Кастомная модель пользователя с ролями.

Согласно ТЗ системы выделяются три роли:
- Посетитель (анонимный, не хранится в БД)
- Редактор (editor) — работает через админку, видит только свои ленты
- Администратор (admin) — полный доступ через админку
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользователь системы единого информационного окна."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        EDITOR = "editor", "Редактор"

    role = models.CharField(
        verbose_name="Роль",
        max_length=16,
        choices=Role.choices,
        default=Role.EDITOR,
        help_text="Определяет уровень доступа пользователя в системе",
    )

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        """Является ли пользователь администратором CMS (включая суперпользователя)."""
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_editor_role(self):
        return self.role == self.Role.EDITOR and not self.is_superuser

    def save(self, *args, **kwargs):
        # Суперпользователь всегда администратор CMS
        if self.is_superuser and self.role != self.Role.ADMIN:
            self.role = self.Role.ADMIN

        # Любая роль (админ или редактор) обязана иметь доступ в админку
        if not self.is_staff:
            self.is_staff = True

        super().save(*args, **kwargs)
