"""
Модели навигации сайта.

HeaderLink — отдельный пункт меню в шапке сайта.
Привязан к блоку HeaderLinksBlock, чтобы можно было размещать меню
на разных страницах независимо.
"""

from django.db import models

from blocks.models import HeaderLinksBlock
from pages.models import Page


class HeaderLink(models.Model):
    """Пункт меню в шапке сайта."""

    block = models.ForeignKey(
        HeaderLinksBlock,
        verbose_name="Блок меню",
        related_name="links",
        on_delete=models.CASCADE,
    )

    target_page = models.ForeignKey(
        Page,
        verbose_name="Целевая страница системы",
        related_name="header_links",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Если задана — ссылка ведёт на внутреннюю страницу",
    )
    external_url = models.URLField(
        verbose_name="Внешний URL",
        blank=True,
        help_text="Заполните, если ссылка ведёт на внешний ресурс",
    )

    title = models.CharField(verbose_name="Заголовок пункта меню", max_length=128)
    position = models.PositiveIntegerField(
        verbose_name="Порядок",
        default=0,
        db_index=True,
    )
    is_visible = models.BooleanField(verbose_name="Виден на сайте", default=True)
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"
        ordering = ["position", "id"]

    def __str__(self):
        return self.title

    @property
    def resolved_url(self):
        """Возвращает URL, на который ведёт пункт меню."""
        if self.target_page:
            return f"/{self.target_page.slug}/"
        return self.external_url or "#"
