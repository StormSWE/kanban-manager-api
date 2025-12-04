from rest_framework.permissions import BasePermission, IsAuthenticated


class IsOwner(BasePermission):
    """Allow access only to the owner of the object."""

    message = "You can only access your own profile."

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", obj)
        return bool(request.user and request.user.is_authenticated and owner == request.user)


__all__ = ["IsAuthenticated", "IsOwner"]
