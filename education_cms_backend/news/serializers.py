"""Сериализаторы публикаций."""

from rest_framework import serializers

from .models import Post


class PostShortSerializer(serializers.ModelSerializer):
    """Краткая версия — используется при встраивании ленты в страницу."""

    author = serializers.CharField(source="author.username", read_only=True, default=None)
    image = serializers.ImageField(read_only=True)
    published_at = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "image",
            "tags",
            "is_urgent",
            "author",
            "published_at",
        )

    def get_published_at(self, obj):
        return obj.effective_published_at


class PostSerializer(serializers.ModelSerializer):
    """Полная версия — используется на эндпоинте /api/news/."""

    author = serializers.CharField(source="author.username", read_only=True, default=None)
    image = serializers.ImageField(read_only=True)
    published_at = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "news_feed",
            "title",
            "content",
            "image",
            "tags",
            "is_urgent",
            "author",
            "published_at",
            "created_at",
            "updated_at",
        )

    def get_published_at(self, obj):
        return obj.effective_published_at