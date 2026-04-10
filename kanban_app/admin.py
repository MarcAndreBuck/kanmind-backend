from django.contrib import admin
from .models import Board, Task, Comment


class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner")
    search_fields = ("title", "owner__email")
    filter_horizontal = ("members",)


class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "board", "status", "priority", "assignee", "reviewer")
    list_filter = ("status", "priority")
    search_fields = ("title", "description")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "author", "created_at")
    search_fields = ("task__title", "author__email")


admin.site.register(Board, BoardAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)