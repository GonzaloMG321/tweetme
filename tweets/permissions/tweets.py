"""Tweet permissions classes"""

# Django Rest Framework
from rest_framework.permissions import BasePermission

# Models 

class IsOwnerTweet(BasePermission):
    """"Verifica si el usuario creó el tweet"""
    def has_permission(self, request, view):
        obj = view.get_object()
        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
