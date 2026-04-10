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
        if self.action == "retrieve":
            return BoardRetrieveSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer
        return BoardListSerializer

    def get_queryset(self):
        user = self.request.user

        if self.action == "list":
            if user.is_staff:
                return Board.objects.all()

            return Board.objects.filter(
                Q(owner=user) | Q(members=user)
            ).distinct()

        return Board.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
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
        serializer.save(creator=self.request.user)

    def assigned_to_me(self, request):
        tasks = Task.objects.filter(assignee=request.user).distinct()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def reviewing(self, request):
        tasks = Task.objects.filter(reviewer=request.user).distinct()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_task(self, task_id):
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return None

    def user_can_access_task(self, task, user):
        return (
            user.is_staff
            or task.board.owner == user
            or task.board.members.filter(id=user.id).exists()
        )

    def get(self, request, task_id):
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
        try:
            return Comment.objects.get(id=comment_id, task_id=task_id)
        except Comment.DoesNotExist:
            return None

    def delete(self, request, task_id, comment_id):
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
