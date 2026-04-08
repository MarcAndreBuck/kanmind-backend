from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBoardOwnerMemberOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff:
            return True

        if request.method in SAFE_METHODS:
            return obj.owner == user or obj.members.filter(id=user.id).exists()

        if request.method in ["PUT", "PATCH"]:
            return obj.owner == user or obj.members.filter(id=user.id).exists()

        if request.method == "DELETE":
            return obj.owner == user

        return False


class IsBoardMemberForTask(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if view.action == "create":
            board_id = request.data.get("board")

            if not board_id:
                return False

            from kanban_app.models import Board

            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                return False

            return (
                board.owner == user
                or board.members.filter(id=user.id).exists()
            )

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff:
            return True

        if request.method in SAFE_METHODS:
            return (
                obj.board.owner == user
                or obj.board.members.filter(id=user.id).exists()
            )

        if request.method in ["PATCH"]:
            return (
                obj.board.owner == user
                or obj.board.members.filter(id=user.id).exists()
            )

        if request.method == "DELETE":
            return obj.creator == user or obj.board.owner == user

        return False
