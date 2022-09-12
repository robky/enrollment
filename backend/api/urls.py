from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import ImportsViewSet, NodesViewSet

app_name = "api"
router = DefaultRouter(trailing_slash=False)
router.register("imports", ImportsViewSet, basename="imports")
router.register("nodes", NodesViewSet, basename="nodes")

urlpatterns = [
    path("", include(router.urls)),
]
