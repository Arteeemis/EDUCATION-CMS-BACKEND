"""
Модели блоков для визуального конструктора страниц.

Реализованы по паттерну Class Table Inheritance через django-polymorphic:
- Block — базовая модель с общими полями
- Наследники — конкретные типы блоков с дополнительными полями
"""

from django.conf import settings
from django.db import models
from polymorphic.models import PolymorphicModel


# ---------------------------------------------------------------------------
# Базовый блок (супертип)
# ---------------------------------------------------------------------------
class Block(PolymorphicModel):
    """Базовая модель для всех блоков конструктора.

    Соответствует таблице `blocks` на ER-диаграмме.
    Каждый наследник создаёт собственную таблицу в БД (CTI).
    """

    type = models.CharField(
        verbose_name="Тип блока",
        max_length=32,
        editable=False,
        help_text="Технический идентификатор типа блока",
    )
    admin_label = models.CharField(
        verbose_name="Название в системе",
        max_length=128,
        blank=True,
        help_text="Подпись блока в списке для удобства администратора",
    )
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Обновлён", auto_now=True)

    class Meta:
        verbose_name = "Блок"
        verbose_name_plural = "Блоки (все типы)"
        ordering = ["-created_at"]

    def __str__(self):
        label = self.admin_label or self.get_type_display()
        return f"#{self.pk} {label}"

    def save(self, *args, **kwargs):
        # Автоматически проставляем технический тип на основе класса
        if not self.type:
            self.type = self._meta.model_name
        super().save(*args, **kwargs)

    def get_type_display(self):
        return self._meta.verbose_name


# ---------------------------------------------------------------------------
# HTML-блок
# ---------------------------------------------------------------------------
class HtmlBlock(Block):
    """Блок с произвольным HTML-содержимым."""

    html_content = models.TextField(
        verbose_name="HTML-содержимое",
        help_text="Произвольный HTML-код, который будет вставлен на страницу",
    )

    class Meta:
        verbose_name = "HTML-блок"
        verbose_name_plural = "HTML-блоки"


# ---------------------------------------------------------------------------
# FAQ-блок и вопросы
# ---------------------------------------------------------------------------
class FaqBlock(Block):
    """Блок «Часто задаваемые вопросы». Содержит набор пар вопрос-ответ."""

    title = models.CharField(verbose_name="Заголовок блока", max_length=255)

    class Meta:
        verbose_name = "FAQ-блок"
        verbose_name_plural = "FAQ-блоки"


class Question(models.Model):
    """Один вопрос-ответ внутри FAQ-блока."""

    faq_block = models.ForeignKey(
        FaqBlock,
        verbose_name="FAQ-блок",
        related_name="questions",
        on_delete=models.CASCADE,
    )
    question = models.TextField(verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    position = models.PositiveIntegerField(
        verbose_name="Порядок отображения",
        default=0,
        db_index=True,
    )
    created_at = models.DateTimeField(verbose_name="Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["position", "id"]

    def __str__(self):
        return self.question[:80]


# ---------------------------------------------------------------------------
# Новостная лента (блок-контейнер)
# ---------------------------------------------------------------------------
class NewsFeed(Block):
    """Блок-контейнер для новостной ленты.

    Сами посты живут в приложении `news` и привязаны к этому блоку.
    К ленте может быть прикреплён один или несколько редакторов,
    которые получают право публиковать посты именно в этой ленте.
    """

    title = models.CharField(verbose_name="Заголовок ленты", max_length=255)

    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Редакторы ленты",
        related_name="news_feeds",
        blank=True,
        help_text="Пользователи с ролью «Редактор», которым разрешено "
        "публиковать посты в этой ленте",
    )

    class Meta:
        verbose_name = "Новостная лента"
        verbose_name_plural = "Новостные ленты"


# ...existing code...


class GoogleDocBlock(Block):
    """Блок Google документа."""

    doc_url = models.URLField(
        verbose_name="Ссылка на Google Документ",
        help_text="Вставьте публичную ссылку или embed-код Google Docs",
    )

    class Meta:
        verbose_name = "Блок Google документа"
        verbose_name_plural = "Блоки Google документов"


class GoogleSheetBlock(Block):
    """Блок Google таблицы."""

    table_url = models.URLField(
        verbose_name="Ссылка на Google Таблицу",
        help_text="Вставьте публичную ссылку или embed-код таблицы",
    )

    class Meta:
        verbose_name = "Блок Google таблицы"
        verbose_name_plural = "Блоки Google таблиц"


class VkVideoBlock(Block):
    """Блок VK видео."""

    video_url = models.URLField(
        verbose_name="Ссылка на VK видео",
        help_text="Публичная ссылка на видео VK",
    )

    class Meta:
        verbose_name = "Блок VK видео"
        verbose_name_plural = "Блоки VK видео"


class LinksBlock(Block):
    """Блок с набором ссылок."""

    title = models.CharField(
        verbose_name="Название блока с ссылками",
        max_length=255,
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True,
    )
    link1 = models.URLField(verbose_name="Ссылка №1")
    link1_desc = models.CharField(
        verbose_name="Описание ссылки №1", max_length=255, blank=True, null=True
    )
    link2 = models.URLField(verbose_name="Ссылка №2", blank=True, null=True)
    link2_desc = models.CharField(
        verbose_name="Описание ссылки №2", max_length=255, blank=True, null=True
    )
    link3 = models.URLField(verbose_name="Ссылка №3", blank=True, null=True)
    link3_desc = models.CharField(
        verbose_name="Описание ссылки №3", max_length=255, blank=True, null=True
    )
    link4 = models.URLField(verbose_name="Ссылка №4", blank=True, null=True)
    link4_desc = models.CharField(
        verbose_name="Описание ссылки №4", max_length=255, blank=True, null=True
    )
    link5 = models.URLField(verbose_name="Ссылка №5", blank=True, null=True)
    link5_desc = models.CharField(
        verbose_name="Описание ссылки №5", max_length=255, blank=True, null=True
    )
    link6 = models.URLField(verbose_name="Ссылка №6", blank=True, null=True)
    link6_desc = models.CharField(
        verbose_name="Описание ссылки №6", max_length=255, blank=True, null=True
    )

    class Meta:
        verbose_name = "Блок ссылок"
        verbose_name_plural = "Блоки ссылок"


# ---------------------------------------------------------------------------
# Меню в шапке (блок-контейнер)
# ---------------------------------------------------------------------------
class HeaderLinksBlock(Block):
    """Блок-контейнер для пунктов меню в шапке сайта.

    Сами пункты меню — отдельная модель HeaderLink, привязанная к этому блоку.
    """

    class Meta:
        verbose_name = "Меню (шапка)"
        verbose_name_plural = "Меню (шапка)"


# ---------------------------------------------------------------------------
# Контакты в подвале (блок)
# ---------------------------------------------------------------------------
class FooterContactsBlock(Block):
    """Блок «Контакты», размещаемый, как правило, в подвале сайта."""

    address = models.CharField(verbose_name="Адрес", max_length=255, blank=True)
    phone = models.CharField(verbose_name="Телефон", max_length=64, blank=True)
    email = models.EmailField(verbose_name="Email", blank=True)

    open_date = models.DateField(
        verbose_name="Дата начала работы", null=True, blank=True
    )
    close_date = models.DateField(
        verbose_name="Дата окончания работы", null=True, blank=True
    )
    open_time = models.TimeField(verbose_name="Время открытия", null=True, blank=True)
    close_time = models.TimeField(verbose_name="Время закрытия", null=True, blank=True)
    weekends = models.CharField(
        verbose_name="Выходные дни",
        max_length=128,
        blank=True,
        help_text="Например: «Сб, Вс»",
    )

    vk_url = models.URLField(verbose_name="Ссылка ВКонтакте", blank=True)
    tg_url = models.URLField(verbose_name="Ссылка Telegram", blank=True)
    max_url = models.URLField(verbose_name="Ссылка Max", blank=True)

    class Meta:
        verbose_name = "Контакты (подвал)"
        verbose_name_plural = "Контакты (подвал)"
