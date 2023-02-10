from rest_framework import permissions


class IsAuthorOrSuperUser(permissions.BasePermission):
    """Автор, Суперпользователь или ReadOnly"""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user
                and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.user and request.user.is_authenticated
                and (request.user.is_staff
                     or obj.author == request.user or request.method == 'POST'
                     and request.user.is_authenticated)
                or (request.method in permissions.SAFE_METHODS))
