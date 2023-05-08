from rest_framework.permissions import BasePermission

class IsAuthenticatedOrWriteOnly(BasePermission):
    """
    The request is authenticated if the user is authenticated, or if it is a write-only POST request.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True  # allow write requests (POST) without authentication
        return request.user and request.user.is_authenticated  # require authentication for all other requests