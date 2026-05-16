"""
Сериализаторы страниц.

PageListSerializer — для списка страниц (краткая информация).
PageDetailSerializer — для полной страницы с массивом блоков, готовых
к рендеру на фронте.
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
    """Полная страница со всеми видимыми блоками в правильном порядке."""

    blocks = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ("id", "title", "slug", "status", "blocks", "updated_at")

    def get_blocks(self, obj):
        # Берём только видимые размещения, упорядоченные по position
        placements = (
            obj.page_blocks.filter(is_visible=True)
            .select_related("block")
            .order_by("position", "id")
        )
        return PageBlockSerializer(placements, many=True, context=self.context).data