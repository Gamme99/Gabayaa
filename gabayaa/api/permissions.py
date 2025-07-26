from rest_framework import permissions

class IsManager(permissions.BasePermission):
    """
    Allow access only to manager users (is_staff=True)
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a staff user for unsafe methods,
    or is a read-only request for anyone.
    """
    def has_permission(self, request, view):
        # SAFE_METHODS are GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_staff