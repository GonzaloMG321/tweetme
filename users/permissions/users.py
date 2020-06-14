# Django
from rest_framework.permissions import BasePermission

class IsProfileOwner(BasePermission):
    """Allow acces only if the user is the owner of the profile"""
    message = 'No tienes permiso para editar este perfil'

    def has_object_permission(self, request, view, obj):
        return request.user == obj
