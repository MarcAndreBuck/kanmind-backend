from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import NotFound

from kanban_app.models import Board


class IsBoardOwnerMemberOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff:
            return True

        is_board_member = obj.members.filter(id=user.id).exists()
        is_board_owner = obj.owner == user

        if request.method in SAFE_METHODS:
            return is_board_owner or is_board_member

        if request.method in ["PATCH", "PUT"]:
            return is_board_owner or is_board_member

        if request.method == "DELETE":
            return is_board_owner

        return False


class IsBoardMemberForTask(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if view.action == "create":
            board_id = request.data.get("board")

            if not board_id:
                return True

            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                raise NotFound("Board not found.")

            return board.owner == user or board.members.filter(id=user.id).exists()

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff:
            return True

        is_board_member = obj.board.members.filter(id=user.id).exists()
        is_board_owner = obj.board.owner == user

        if request.method in SAFE_METHODS:
            return is_board_owner or is_board_member

        if request.method == "PATCH":
            return is_board_owner or is_board_member

        if request.method == "DELETE":
            return obj.creator == user or is_board_owner

        return False
