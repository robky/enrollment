from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    DeleteViewSet,
    HistoryViewSet,
    ImportsViewSet,
    NodesViewSet,
    UpdatesViewSet,
)

app_name = "api"
router = DefaultRouter(trailing_slash=False)
router.register("imports", ImportsViewSet, basename="imports")
router.register(
    r"node/(?P<node_id>[\w.@+-]+)/history", HistoryViewSet, basename="history"
)
router.register("nodes", NodesViewSet, basename="nodes")
router.register("updates", UpdatesViewSet, basename="updates")
router.register("delete", DeleteViewSet, basename="delete")


urlpatterns = [
    path("", include(router.urls)),
]
