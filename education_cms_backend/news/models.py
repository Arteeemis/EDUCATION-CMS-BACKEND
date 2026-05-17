"""
Модели для новостной ленты.

Один пост (Post) принадлежит одной новостной ленте (NewsFeed из приложения blocks)
и имеет автора (пользователя).
"""

from django.conf import settings
from django.db import models

from blocks.models import NewsFeed


class Post(models.Model):
    """Публикация в новостной ленте."""

    news_feed = models.ForeignKey(
        NewsFeed,
        verbose_name="Новостная лента",
        related_name="posts",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        related_name="posts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    title = models.CharField(verbose_name="Заголовок", max_length=255)
    content = models.TextField(verbose_name="Содержимое", blank=True)
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="posts/%Y/%m/",
        blank=True,
        null=True,
    )
    tags = models.CharField(
        verbose_name="Теги",
        max_length=255,
        blank=True,
        help_text="Через запятую, например: важно, новости, ИУ-5",
    )
    # Поле в БД остаётся is_urgent — не ломаем миграции.
    # Меняем только отображаемое название на «Важная публикация».
    is_urgent = models.BooleanField(
        verbose_name="Важная публикация",
        default=False,
        help_text="Важные публикации выделяются в ленте",
    )
    published_at = models.DateTimeField(
        verbose_name="Дата публикации",
        null=True,
        blank=True,
        help_text="Если не указана, используется дата создания",
    )
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ["-is_urgent", "-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["-published_at"]),
            models.Index(fields=["news_feed", "-published_at"]),
        ]

    def __str__(self):
        return self.title

    @property
    def effective_published_at(self):
        return self.published_at or self.created_at
