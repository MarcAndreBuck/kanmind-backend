from django.contrib.auth.models import User
from rest_framework import serializers

from kanban_app.models import Board, Comment, Task


class BoardMemberSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        """Return the full name of the user from their profile.

        Retrieves the fullname field from the associated UserProfile.
        Used for serializing user data with full name.
        """
        return obj.profile.fullname


class BoardListSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def get_member_count(self, obj):
        """Return the number of members in the board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the total number of tasks in the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks with status 'to-do'."""
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of tasks with high priority."""
        return obj.tasks.filter(priority="high").count()


class BoardRetrieveSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = BoardMemberSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    def get_tasks(self, obj):
        """Return serialized data for all tasks in the board."""
        return TaskSerializer(obj.tasks.all(), many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
        write_only=True,
    )
    owner_data = serializers.SerializerMethodField()
    members_data = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "members", "owner_data", "members_data"]

    def get_owner_data(self, obj):
        """Return the owner's id, email, and full name."""
        return {
            "id": obj.owner.id,
            "email": obj.owner.email,
            "fullname": obj.owner.profile.fullname,
        }

    def get_members_data(self, obj):
        """Return a list of members' id, email, and full name."""
        return [
            {
                "id": user.id,
                "email": user.email,
                "fullname": user.profile.fullname,
            }
            for user in obj.members.all()
        ]

    def update(self, instance, validated_data):
        """Update the board instance with validated data, including members."""
        members = validated_data.pop("members", None)
        instance.title = validated_data.get("title", instance.title)
        instance.save()

        if members is not None:
            instance.members.set(members)

        return instance


class TaskSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    assignee = BoardMemberSerializer(read_only=True)
    reviewer = BoardMemberSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        """Return the number of comments on the task."""
        return obj.comments.count()

    def validate(self, attrs):
        """Validate the task data, ensuring assignee and reviewer are board members."""
        board = attrs.get("board") or getattr(self.instance, "board", None)
        assignee = attrs.get("assignee")
        reviewer = attrs.get("reviewer")

        if assignee and assignee != board.owner and not board.members.filter(id=assignee.id).exists():
            raise serializers.ValidationError(
                {"assignee_id": "Assignee must be a board member."}
            )

        if reviewer and reviewer != board.owner and not board.members.filter(id=reviewer.id).exists():
            raise serializers.ValidationError(
                {"reviewer_id": "Reviewer must be a board member."}
            )

        if self.instance and "board" in attrs:
            raise serializers.ValidationError(
                {"board": "Changing the board is not allowed."}
            )

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]

    def get_author(self, obj):
        """Return the full name of the comment author."""
        return obj.author.profile.fullname


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content"]
