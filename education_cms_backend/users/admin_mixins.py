"""
Миксины для разграничения доступа к разделам админки по ролям.

Использование:
    class MyModelAdmin(AdminOnlyMixin, admin.ModelAdmin):
        ...

    class MyReadOnlyAdmin(AdminWriteEditorReadMixin, admin.ModelAdmin):
        ...
"""


class AdminOnlyMixin:
    """Раздел админки доступен только администратору.

    Используется для разделов, к которым редактор не имеет доступа:
    страницы, блоки, навигация, пользователи.
    """

    def _is_admin(self, request):
        return request.user.is_authenticated and request.user.is_admin_role

    def has_module_permission(self, request):
        return self._is_admin(request)

    def has_view_permission(self, request, obj=None):
        return self._is_admin(request)

    def has_add_permission(self, request):
        return self._is_admin(request)

    def has_change_permission(self, request, obj=None):
        return self._is_admin(request)

    def has_delete_permission(self, request, obj=None):
        return self._is_admin(request)


class AdminWriteEditorReadMixin:
    """Администратор имеет полный доступ, редактор — только просмотр.

    Используется для NewsFeed: редактор должен видеть свои ленты,
    чтобы понимать контекст, но не может их редактировать.
    """

    def _is_admin(self, request):
        return request.user.is_authenticated and request.user.is_admin_role

    def _is_editor(self, request):
        return request.user.is_authenticated and request.user.is_editor_role

    def has_module_permission(self, request):
        return self._is_admin(request) or self._is_editor(request)

    def has_view_permission(self, request, obj=None):
        return self._is_admin(request) or self._is_editor(request)

    def has_add_permission(self, request):
        return self._is_admin(request)

    def has_change_permission(self, request, obj=None):
        return self._is_admin(request)

    def has_delete_permission(self, request, obj=None):
        return self._is_admin(request)