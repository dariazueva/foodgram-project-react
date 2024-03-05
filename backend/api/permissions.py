from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """Доступ только для админов, остальным только чтение."""

    def has_object_permission(self, request, view, obj):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_staff
            )


class AuthorAdminOrReadOnly(permissions.BasePermission):
    """Доступ только для админа и автора, остальным только чтение."""

    def has_object_permission(self, request, view, obj):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (request.user.is_staff or request.user == obj.author)
            )
