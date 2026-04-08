from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from kanban_app.api.permissions import IsBoardMemberForTask
from kanban_app.api.serializers import (
    BoardListSerializer,
    BoardRetrieveSerializer,
    BoardUpdateSerializer,
    TaskSerializer,
)
from kanban_app.models import Board, Task


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Board.objects.all()

        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardRetrieveSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer 
        return BoardListSerializer

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberForTask]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def assigned_to_me(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def reviewing(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)