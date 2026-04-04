from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from kanban_app.api.serializers import (
    BoardListSerializer,
    BoardRetrieveSerializer,
    BoardUpdateSerializer,
)
from kanban_app.models import Board


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
