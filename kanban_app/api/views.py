from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from kanban_app.api.permissions import (
    IsBoardMemberForTask,
    IsBoardOwnerMemberOrAdmin,
)
from kanban_app.api.serializers import (
    BoardListSerializer,
    BoardRetrieveSerializer,
    BoardUpdateSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    TaskSerializer,
)
from kanban_app.models import Board, Comment, Task


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardOwnerMemberOrAdmin]

    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action.

        Uses BoardRetrieveSerializer for retrieve action.
        Uses BoardUpdateSerializer for partial_update action.
        Defaults to BoardListSerializer for other actions.
        """
        if self.action == "retrieve":
            return BoardRetrieveSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer
        return BoardListSerializer

    def get_queryset(self):
        """Return the queryset of boards based on user permissions.

        For list action, returns all boards if user is staff.
        Otherwise, returns boards where user is owner or member.
        For other actions, returns all boards.
        """
        user = self.request.user

        if self.action == "list":
            if user.is_staff:
                return Board.objects.all()

            return Board.objects.filter(
                Q(owner=user) | Q(members=user)
            ).distinct()

        return Board.objects.all()

    def perform_create(self, serializer):
        """Create a new board with the current user as owner.

        Saves the board instance using the serializer.
        Sets the requesting user as the board owner.
        """
        serializer.save(owner=self.request.user)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        """Return the queryset of tasks based on user permissions and action."""
        user = self.request.user

        if self.action == "list":
            return Task.objects.none()

        if self.action in ["assigned_to_me", "reviewing"]:
            if user.is_staff:
                return Task.objects.all()

            return Task.objects.filter(
                Q(board__owner=user) | Q(board__members=user)
            ).distinct()

        return Task.objects.all()

    def perform_create(self, serializer):
        """Create a new task with the current user as creator."""
        serializer.save(creator=self.request.user)

    def assigned_to_me(self, request):
        """Return tasks assigned to the current user."""
        tasks = Task.objects.filter(assignee=request.user).distinct()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def reviewing(self, request):
        """Return tasks where the current user is the reviewer.

        Retrieves all tasks assigned to the user for review.
        Returns serialized task data in the response.
        """
        tasks = Task.objects.filter(reviewer=request.user).distinct()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_task(self, task_id):
        """Retrieve a task by its ID.

        Attempts to get the task from the database.
        Returns the task object if found, otherwise None.
        """
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return None

    def user_can_access_task(self, task, user):
        """Check if the user has access to the task.

        Grants access if the user is staff, board owner, or board member.
        Returns True if access is allowed, False otherwise.
        """
        return (
            user.is_staff
            or task.board.owner == user
            or task.board.members.filter(id=user.id).exists()
        )

    def get(self, request, task_id):
        """Retrieve all comments for a specific task.

        Checks if the task exists and user has access.
        Returns serialized comment data or appropriate error response.
        """
        task = self.get_task(task_id)

        if task is None:
            return Response(
                {"detail": "Task not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not self.user_can_access_task(task, request.user):
            return Response(
                {"detail": "You do not have permission to view comments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, task_id):
        """Create a new comment for a specific task.

        Validates task existence and user access.
        Serializes and saves the comment with the current user as author.
        Returns the created comment data or error response.
        """
        task = self.get_task(task_id)

        if task is None:
            return Response(
                {"detail": "Task not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not self.user_can_access_task(task, request.user):
            return Response(
                {"detail": "You do not have permission to add comments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CommentCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save(task=task, author=request.user)
        response_serializer = CommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TaskCommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_comment(self, task_id, comment_id):
        """Retrieve a specific comment by task and comment ID.

        Attempts to get the comment from the database.
        Returns the comment object if found, otherwise None.
        """
        try:
            return Comment.objects.get(id=comment_id, task_id=task_id)
        except Comment.DoesNotExist:
            return None

    def delete(self, request, task_id, comment_id):
        """Delete a specific comment.

        Checks if the comment exists and user has permission to delete.
        Only the author or staff can delete the comment.
        Returns appropriate response or error.
        """
        comment = self.get_comment(task_id, comment_id)

        if comment is None:
            return Response(
                {"detail": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user != comment.author and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
