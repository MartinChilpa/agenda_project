from rest_framework.permissions import BasePermission


class IsProvider(BasePermission):
    message = 'Solo los profesionales pueden administrar una agenda.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.role == 'PROVIDER')
        )
