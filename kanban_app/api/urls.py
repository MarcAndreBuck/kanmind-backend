from rest_framework.routers import DefaultRouter

from kanban_app.api.views import BoardViewSet

router = DefaultRouter()
router.register("boards", BoardViewSet, basename="board")

urlpatterns = router.urls
