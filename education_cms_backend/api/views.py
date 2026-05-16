"""
Публичные REST API эндпоинты.

Все эндпоинты — read-only (GET). Доступны без аутентификации.
Запись данных выполняется через админ-интерфейс.
"""

from rest_framework import viewsets, mixins, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from blocks.models import FooterContactsBlock, HeaderLinksBlock
from blocks.serializers import (
    FooterContactsBlockSerializer,
    HeaderLinksBlockSerializer,
)
from news.models import Post
from news.serializers import PostSerializer
from pages.models import Page
from pages.serializers import PageListSerializer, PageDetailSerializer


# ---------------------------------------------------------------------------
# Страницы
# ---------------------------------------------------------------------------
class PageViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Публичные страницы сайта.

    list:   GET /api/pages/             — список опубликованных страниц
    detail: GET /api/pages/<slug>/      — полная страница с блоками
    """

    queryset = Page.objects.filter(status=Page.Status.PUBLISHED)
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PageDetailSerializer
        return PageListSerializer


# ---------------------------------------------------------------------------
# Публикации
# ---------------------------------------------------------------------------
class PostViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Публикации новостных лент.

    list:   GET /api/news/                       — все публикации (пагинация)
            GET /api/news/?news_feed=<id>        — публикации конкретной ленты
            GET /api/news/?is_urgent=true        — только срочные
    detail: GET /api/news/<id>/                  — одна публикация
    """

    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Post.objects.select_related("news_feed", "author").all()

        news_feed_id = self.request.query_params.get("news_feed")
        if news_feed_id:
            qs = qs.filter(news_feed_id=news_feed_id)

        is_urgent = self.request.query_params.get("is_urgent")
        if is_urgent is not None:
            qs = qs.filter(is_urgent=is_urgent.lower() in ("true", "1", "yes"))

        return qs


# ---------------------------------------------------------------------------
# Контакты в подвале
# ---------------------------------------------------------------------------
class FooterView(generics.GenericAPIView):
    """Контакты для отображения в подвале сайта.

    Если в системе несколько блоков FooterContactsBlock — отдаётся самый
    свежий по дате создания. Если ни одного нет — 404.

    GET /api/footer/
    """

    serializer_class = FooterContactsBlockSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        footer = FooterContactsBlock.objects.order_by("-created_at").first()
        if footer is None:
            raise NotFound("Блок контактов не настроен.")
        serializer = self.get_serializer(footer)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Меню в шапке
# ---------------------------------------------------------------------------
class HeaderMenuView(generics.GenericAPIView):
    """Меню для шапки сайта.

    Отдаётся самый свежий блок HeaderLinksBlock с его видимыми ссылками.

    GET /api/header-menu/
    """

    serializer_class = HeaderLinksBlockSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        menu = HeaderLinksBlock.objects.order_by("-created_at").first()
        if menu is None:
            raise NotFound("Меню не настроено.")
        serializer = self.get_serializer(menu)
        return Response(serializer.data)
