"""
Модели страниц сайта.

- Page — страница, имеющая слаг и статус
- PageBlock — связь страницы с блоком (M:N с порядком и видимостью)
"""

from django.db import models

from blocks.models import Block


class Page(models.Model):
    """Страница сайта, формируемая из набора блоков."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PUBLISHED = "published", "Опубликована"

    title = models.CharField(verbose_name="Заголовок", max_length=255)
    slug = models.SlugField(
        verbose_name="URL-адрес (slug)",
        max_length=255,
        unique=True,
        help_text="Уникальный адрес страницы, например 'about' для /about/",
    )
    status = models.CharField(
        verbose_name="Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(verbose_name="Создана", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлена", auto_now=True)

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} (/{self.slug}/)"

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED


class PageBlock(models.Model):
    """Размещение блока на странице.

    Связующая таблица для отношения «многие ко многим» между Page и Block.
    Хранит порядок и видимость.
    """

    page = models.ForeignKey(
        Page,
        verbose_name="Страница",
        related_name="page_blocks",
        on_delete=models.CASCADE,
    )
    block = models.ForeignKey(
        Block,
        verbose_name="Блок",
        related_name="placements",
        on_delete=models.CASCADE,
    )
    position = models.PositiveIntegerField(
        verbose_name="Порядок",
        default=0,
        db_index=True,
    )
    is_visible = models.BooleanField(
        verbose_name="Виден на сайте",
        default=True,
        help_text="Снимите галочку, чтобы временно скрыть блок без удаления",
    )

    class Meta:
        verbose_name = "Блок на странице"
        verbose_name_plural = "Блоки на странице"
        ordering = ["position", "id"]
        unique_together = [("page", "block")]

    def __str__(self):
        return f"{self.page.title} → {self.block} (поз. {self.position})"
