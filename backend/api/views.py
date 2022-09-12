from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from api.serializers import NodesImportsSerializer, NodesSerializer
from core.models import FileSystem


class NodesViewSet(ReadOnlyModelViewSet):
    queryset = FileSystem.objects.root_nodes()
    serializer_class = NodesSerializer


class ImportsViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = NodesImportsSerializer

    def create(self, request, *args, **kwargs):
        return Response({"value": "Данные получены"})
