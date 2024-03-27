from rest_framework import permissions

class CustomPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # Allow GET requests without authentication
        if request.method == 'GET':
            return True
        # Require authentication for POST and PUT requests
        return request.user and request.user.is_authenticated
