from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    DeleteViewSet,
    ImportsViewSet,
    NodesViewSet,
    UpdatesViewSet,
)

app_name = "api"
router = DefaultRouter(trailing_slash=False)
router.register("imports", ImportsViewSet, basename="imports")
router.register("nodes", NodesViewSet, basename="nodes")
router.register("updates", UpdatesViewSet, basename="updates")
router.register("delete", DeleteViewSet, basename="delete")


urlpatterns = [
    path("", include(router.urls)),
]
