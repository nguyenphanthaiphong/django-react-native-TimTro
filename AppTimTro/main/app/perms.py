from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Chỉ cho phép chủ sở hữu của đối tượng thực hiện các thao tác không an toàn (PUT, DELETE)
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_landlord == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'


class IsLandlordUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'landlord'


class IsTenantUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'tenant'