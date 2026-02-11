
from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    Assumes the model instance has a `user` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # if request.method in permissions.SAFE_METHODS:
        #    return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_staff or getattr(request.user.profile, 'is_admin', lambda: False)())

class IsDeveloperUser(permissions.BasePermission):
    """
    Allows access only to developer users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (getattr(request.user.profile, 'is_developer', lambda: False)())
