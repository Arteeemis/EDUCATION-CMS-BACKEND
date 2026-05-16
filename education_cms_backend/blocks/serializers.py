"""
Сериализаторы блоков.

Ключевая особенность — полиморфная сериализация:
PolymorphicBlockSerializer выбирает нужный сериализатор по типу
конкретного блока. Это позволяет отдавать страницу со списком
блоков, где у каждого блока свой набор полей.
"""

from rest_framework import serializers

from .models import (
    Block,
    HtmlBlock,
    FaqBlock,
    Question,
    NewsFeed,
    HeaderLinksBlock,
    FooterContactsBlock,
)


# ---------------------------------------------------------------------------
# HTML-блок
# ---------------------------------------------------------------------------
class HtmlBlockSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = HtmlBlock
        fields = ("id", "type", "admin_label", "html_content")

    def get_type(self, obj):
        return "html"


# ---------------------------------------------------------------------------
# FAQ-блок
# ---------------------------------------------------------------------------
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "question", "answer", "position")


class FaqBlockSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = FaqBlock
        fields = ("id", "type", "admin_label", "title", "questions")

    def get_type(self, obj):
        return "faq"


# ---------------------------------------------------------------------------
# Новостная лента (превью + ссылка на пагинированный список)
# ---------------------------------------------------------------------------
class NewsFeedSerializer(serializers.ModelSerializer):
    """Сериализатор ленты для встраивания в страницу.

    Отдаём только превью (последние N постов) + общее количество
    и URL для пагинации остальных. Полные посты живут на /api/news/.
    """

    PREVIEW_LIMIT = 5

    type = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    posts_total = serializers.SerializerMethodField()
    posts_url = serializers.SerializerMethodField()

    class Meta:
        model = NewsFeed
        fields = (
            "id",
            "type",
            "admin_label",
            "title",
            "posts",
            "posts_total",
            "posts_url",
        )

    def get_type(self, obj):
        return "news_feed"

    def get_posts(self, obj):
        # Импорт внутри метода во избежание циклической зависимости
        from news.serializers import PostShortSerializer

        recent = obj.posts.all()[: self.PREVIEW_LIMIT]
        return PostShortSerializer(recent, many=True, context=self.context).data

    def get_posts_total(self, obj):
        return obj.posts.count()

    def get_posts_url(self, obj):
        request = self.context.get("request")
        path = f"/api/news/?news_feed={obj.pk}"
        return request.build_absolute_uri(path) if request else path


# ---------------------------------------------------------------------------
# Меню в шапке (контейнер ссылок)
# ---------------------------------------------------------------------------
class HeaderLinksBlockSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()

    class Meta:
        model = HeaderLinksBlock
        fields = ("id", "type", "admin_label", "links")

    def get_type(self, obj):
        return "header_links"

    def get_links(self, obj):
        from navigation.serializers import HeaderLinkSerializer

        visible_links = obj.links.filter(is_visible=True)
        return HeaderLinkSerializer(visible_links, many=True, context=self.context).data


# ---------------------------------------------------------------------------
# Контакты в подвале
# ---------------------------------------------------------------------------
class FooterContactsBlockSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = FooterContactsBlock
        fields = (
            "id",
            "type",
            "admin_label",
            "address",
            "phone",
            "email",
            "open_date",
            "close_date",
            "open_time",
            "close_time",
            "weekends",
            "vk_url",
            "tg_url",
            "max_url",
        )

    def get_type(self, obj):
        return "footer_contacts"


# ---------------------------------------------------------------------------
# Полиморфный сериализатор блоков — диспетчер
# ---------------------------------------------------------------------------
class PolymorphicBlockSerializer(serializers.Serializer):
    """Сериализатор, который выбирает нужный конкретный сериализатор
    в зависимости от реального типа полиморфного блока.

    Используется для отдачи списка блоков на странице.
    """

    SERIALIZER_MAP = {
        HtmlBlock: HtmlBlockSerializer,
        FaqBlock: FaqBlockSerializer,
        NewsFeed: NewsFeedSerializer,
        HeaderLinksBlock: HeaderLinksBlockSerializer,
        FooterContactsBlock: FooterContactsBlockSerializer,
    }

    def to_representation(self, instance):
        # PolymorphicModel автоматически возвращает дочерний объект
        # при обращении к атрибуту, но для надёжности приводим явно
        real_instance = (
            instance.get_real_instance() if isinstance(instance, Block) else instance
        )
        serializer_class = self.SERIALIZER_MAP.get(real_instance.__class__)
        if serializer_class is None:
            return {
                "id": real_instance.pk,
                "type": "unknown",
                "error": f"No serializer for {real_instance.__class__.__name__}",
            }
        return serializer_class(real_instance, context=self.context).data
