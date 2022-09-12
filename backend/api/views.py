from rest_framework import mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from api.serializers import NodesImportsSerializer, NodesSerializer
from core.models import (
    FileSystem,
    TYPE_NAME,
    TYPE_FILE,
    TYPE_FOLDER,
    recount_size,
)


class NodesViewSet(ReadOnlyModelViewSet):
    serializer_class = NodesSerializer

    def get_queryset(self):
        if self.action == "list":
            return FileSystem.objects.root_nodes()
        return FileSystem.objects.all()


class ImportsViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = NodesImportsSerializer

    def create(self, request, *args, **kwargs):
        serializer = NodesImportsSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            items_data = serializer.validated_data.get("items")
            update_date = serializer.validated_data.get("updateDate")
            for item in items_data:
                node = None
                type = TYPE_NAME[item["type"]]
                parent = item.get("parentId", None)
                if parent:
                    parent = get_object_or_404(FileSystem, id=parent)
                if type == TYPE_FOLDER:
                    node = FileSystem.objects.create(
                        id=item["id"],
                        type=type,
                        parent=parent,
                        date=update_date,
                    )
                elif type == TYPE_FILE:
                    node = FileSystem.objects.create(
                        id=item["id"],
                        url=item["url"],
                        type=type,
                        parent=parent,
                        size=item["size"],
                        date=update_date,
                    )
                if node:
                    recount_size(instance=node)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
