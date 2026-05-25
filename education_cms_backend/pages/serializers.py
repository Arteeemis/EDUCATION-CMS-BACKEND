"""
Сериализаторы страниц.

PageListSerializer — для списка страниц (краткая информация).
PageDetailSerializer — для полной страницы с массивом блоков, готовых
к рендеру на фронте.

Важно: API отдаёт ВСЕ блоки страницы вместе с их флагом is_visible.
Фильтрация по видимости — ответственность фронта, потому что для разных
типов блоков «невидимость» означает разное (для header/footer — скрыть
глобальный элемент на этой странице, для контентных — не рендерить вовсе).
"""

from rest_framework import serializers

from blocks.serializers import PolymorphicBlockSerializer

from .models import Page, PageBlock


class PageListSerializer(serializers.ModelSerializer):
    """Краткое представление страницы для списка."""

    class Meta:
        model = Page
        fields = ("id", "title", "slug", "status", "updated_at")


class PageBlockSerializer(serializers.ModelSerializer):
    """Размещение блока на странице — отдаёт сам блок через полиморфный сериализатор."""

    block = PolymorphicBlockSerializer(read_only=True)

    class Meta:
        model = PageBlock
        fields = ("position", "is_visible", "block")


class PageDetailSerializer(serializers.ModelSerializer):
    """Полная страница со всеми блоками в правильном порядке.

    Отдаём все блоки, включая невидимые — фронт сам решает, рендерить или
    скрывать, поскольку для header/footer и контентных блоков логика
    «невидимости» различается.
    """

    blocks = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ("id", "title", "slug", "status", "blocks", "updated_at")

    def get_blocks(self, obj):
        placements = obj.page_blocks.select_related("block").order_by("position", "id")
        return PageBlockSerializer(placements, many=True, context=self.context).data
