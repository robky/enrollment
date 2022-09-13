from datetime import datetime, timedelta

from django.db import IntegrityError
from rest_framework import mixins, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from api.serializers import (
    DateTimeSerializer,
    NodesImportsSerializer,
    NodesSerializer,
    NodesUpdateSerializer,
)
from core.models import TYPE_FILE, TYPE_NAME, FileSystem, recount_size_set_data


class NodesViewSet(ReadOnlyModelViewSet):
    serializer_class = NodesSerializer

    def get_queryset(self):
        if self.action == "list":
            return FileSystem.objects.root_nodes()
        return FileSystem.objects.all()


class ImportsViewSet(mixins.CreateModelMixin, GenericViewSet):
    def create(self, request, *args, **kwargs):
        serializer = NodesImportsSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            items_data = serializer.validated_data.get("items")
            update_date = serializer.validated_data.get("updateDate")
            for item in items_data:
                item["date"] = update_date
                item["type"] = TYPE_NAME[item["type"]]
                parent = item.get("parentId", None)
                item.pop("parentId")
                if parent:
                    item["parent"] = get_object_or_404(FileSystem, id=parent)
                try:
                    node = FileSystem.objects.create(**item)
                except IntegrityError:
                    raise ValidationError({"detail": "Ошибка создания"})
                if node:
                    recount_size_set_data(instance=node)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def updates(request):
    date = request.query_params.get("date")
    if date:
        request.data["date"] = date
        serializer = DateTimeSerializer(data=request.data)
        if serializer.is_valid():
            end_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
            one_day_delta = timedelta(hours=24)
            start_date = end_date - one_day_delta
            nodes = FileSystem.objects.filter(
                type=TYPE_FILE, date__range=(start_date, end_date)
            )
            serializer = NodesUpdateSerializer({"items": nodes})
            return Response(serializer.data)
    raise ValidationError({"detail": "Некорректная date"})


@api_view(["DELETE"])
def delete(request, node_id):
    new_date = request.query_params.get("date")
    if new_date:
        node = get_object_or_404(FileSystem, id=node_id)
        request.data["date"] = new_date
        serializer = DateTimeSerializer(data=request.data)
        if serializer.is_valid():
            node.date = new_date
            recount_size_set_data(instance=node, add_operation=False)
            node.delete()
        return Response(status=status.HTTP_200_OK)
    raise ValidationError({"detail": "Некорректное значение"})
