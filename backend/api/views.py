
from rest_framework import mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from api.serializers import NodesImportsSerializer, NodesSerializer
from core.models import FileSystem, TYPE_NAME, TYPE_FILE, TYPE_FOLDER, \
    get_id_from_str


class NodesViewSet(ReadOnlyModelViewSet):
    queryset = FileSystem.objects.root_nodes()
    serializer_class = NodesSerializer


class ImportsViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = NodesImportsSerializer

    def create(self, request, *args, **kwargs):
        serializer = NodesImportsSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid():  # raise_exception=True
            items_data = serializer.validated_data.get("items")
            update_date = serializer.validated_data.get("updateDate")
            for item in items_data:
                type = TYPE_NAME[item['type']]
                if type == TYPE_FOLDER:
                    FileSystem.objects.create(type=type, date=update_date)
                elif type == TYPE_FILE:
                    parent_id = get_id_from_str(item['parentId'])
                    parent = get_object_or_404(FileSystem, id=parent_id)
                    FileSystem.objects.create(
                        url=item['url'],
                        type=type,
                        parent=parent,
                        size=item['size'],
                        date=update_date)
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
