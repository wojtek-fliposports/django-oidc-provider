from rest_framework import permissions
from .common import extract_permissions


class IdTokenHasPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        id_token_permissions = extract_permissions(request.auth)
        required_permissions = set(
            getattr(view, 'required_permissions', list())
        )
        return required_permissions.issubset(id_token_permissions)
