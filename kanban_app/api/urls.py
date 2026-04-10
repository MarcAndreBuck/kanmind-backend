from django.urls import path

from kanban_app.api.views import BoardViewSet, TaskCommentDetailView, TaskCommentView, TaskViewSet

urlpatterns = [
    path(
        "boards/",
        BoardViewSet.as_view({
            "get": "list",
            "post": "create",
        }),
        name="board-list",
    ),
    path(
        "boards/<int:pk>/",
        BoardViewSet.as_view({
            "get": "retrieve",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="board-detail",
    ),
    path(
        "tasks/",
        TaskViewSet.as_view({
            "post": "create",
        }),
        name="task-create",
    ),
    path(
        "tasks/<int:pk>/",
        TaskViewSet.as_view({
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="task-detail",
    ),
    path(
        "tasks/assigned-to-me/",
        TaskViewSet.as_view({
            "get": "assigned_to_me",
        }),
        name="tasks-assigned-to-me",
    ),
    path(
        "tasks/reviewing/",
        TaskViewSet.as_view({
            "get": "reviewing",
        }),
        name="tasks-reviewing",
    ),
    path(
        "tasks/<int:pk>/comments/",
        TaskCommentView.as_view(),
        name="task-comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        TaskCommentDetailView.as_view(),
        name="task-comment-detail",
    ),
]
