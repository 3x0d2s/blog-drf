from rest_framework import permissions


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение для доступа:
    - Чтение доступно всем (включая неавторизованных пользователей).
    - Изменение доступно только владельцам или администраторам.
    """

    def has_permission(self, request, view):
        # Чтение разрешено всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Изменение требует аутентификации
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Изменение разрешено только владельцу объекта или администратору
        if hasattr(obj, "user") and obj.user == request.user:
            return True
        return request.user and request.user.is_staff

