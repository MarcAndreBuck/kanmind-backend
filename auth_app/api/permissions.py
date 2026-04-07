from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBoardOwnerMemberOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff:
            return True

        if request.method in SAFE_METHODS:
            return obj.owner == user or obj.members.filter(id=user.id).exists()

        if request.method == "PATCH":
            return obj.owner == user or obj.members.filter(id=user.id).exists()

        if request.method == "DELETE":
            return obj.owner == user

        return False