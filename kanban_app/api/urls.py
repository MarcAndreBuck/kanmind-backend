from rest_framework.routers import path

from kanban_app.api.views import BoardViewSet

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
]
