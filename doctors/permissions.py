from rest_framework import permissions


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Allows any authenticated user to view doctor records (SAFE_METHODS),
    but restricts update (PUT/PATCH) and delete (DELETE) operations
    strictly to the creator of the record.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.created_by == request.user
