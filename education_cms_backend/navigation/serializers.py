"""Сериализаторы пунктов меню."""

from rest_framework import serializers

from .models import HeaderLink


class HeaderLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = HeaderLink
        fields = ("id", "title", "position", "url", "is_visible")

    def get_url(self, obj):
        return obj.resolved_url
