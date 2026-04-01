from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from kanban_app.api.serializers import BoardSerializer
from kanban_app.models import Board


class BoardViewSet(ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Board.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
