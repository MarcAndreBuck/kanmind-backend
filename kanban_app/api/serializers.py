from rest_framework import serializers
from kanban_app.models import Board

class BoardSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source = "owner.id", read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id"]