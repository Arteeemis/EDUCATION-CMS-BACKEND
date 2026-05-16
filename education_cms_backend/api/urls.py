"""Главный роутер REST API."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PageViewSet, PostViewSet, FooterView, HeaderMenuView

router = DefaultRouter()
router.register(r"pages", PageViewSet, basename="page")
router.register(r"news", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
    path("footer/", FooterView.as_view(), name="footer"),
    path("header-menu/", HeaderMenuView.as_view(), name="header-menu"),
]
