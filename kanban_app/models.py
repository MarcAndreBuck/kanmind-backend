from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    """
    Represents a Kanban board for task management.

    Contains title, owner, and members. Supports multiple tasks.
    Used to organize and manage project workflows.
    """
    title = models.CharField(max_length=255)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )

    members = models.ManyToManyField(
        User,
        related_name="member_boards",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Return the title of the board as its string representation."""
        return self.title


class Task(models.Model):
    """
    Represents a task within a Kanban board.

    Includes details like title, description, status, priority, and assignments.
    Supports workflow tracking from creation to completion.
    """
    STATUS_CHOICES = [
        ("to-do", "To Do"),
        ("in-progress", "In Progress"),
        ("review", "Review"),
        ("done", "Done"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        null=True,
        blank=True,
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="review_tasks",
        null=True,
        blank=True,
    )
    due_date = models.DateField()

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        """Return the title of the task as its string representation."""
        return self.title


class Comment(models.Model):
    """
    Represents a comment on a task.

    Allows users to add notes or discussions to tasks.
    Tracks author and creation time for accountability.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        """Return a string representation of the comment including author and task."""
        return f"Comment by {self.author.profile.fullname} on {self.task.title}"