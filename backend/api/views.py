from datetime import datetime, timedelta

from django.db import IntegrityError
from rest_framework import mixins, status
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
from core.models import (
    TYPE_FILE,
    TYPE_NAME,
    FileSystem,
    History,
    change_size_set_data,
    recount_size_set_data,
    set_position_history,
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
            if not _is_id_unique([item["id"] for item in items_data]):
                raise ValidationError({"detail": "Одинаковые id"})
            if not _is_parents_folders(
                [
                    item["parentId"]
                    for item in items_data
                    if item["parentId"] is not None
                ]
            ):
                raise ValidationError(
                    {"detail": "Родитель должен существовать и быть папкой"}
                )
            update_date = serializer.validated_data.get("updateDate")
            for item in items_data:
                if item.get("size", False) is None:
                    item.pop("size")
                item["date"] = update_date
                item["type"] = TYPE_NAME[item["type"]]
                parent = item.get("parentId", None)
                if parent:
                    item["parent"] = get_object_or_404(FileSystem, id=parent)
                if "parentId" in item:
                    item.pop("parentId")

                if FileSystem.objects.filter(id=item["id"]).exists():
                    node = _update_node(item)
                else:
                    try:
                        node = FileSystem.objects.create(**item)
                    except IntegrityError:
                        raise ValidationError({"detail": "Ошибка создания"})
                    recount_size_set_data(instance=node)

                if node.type == TYPE_FILE:
                    set_position_history(node=node)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _is_id_unique(values: list) -> bool:
    return len(values) == len(set(values))


def _is_parents_folders(values: list) -> bool:
    values = set(values)
    for parent_id in values:
        parent = get_object_or_404(FileSystem, id=parent_id)
        if parent.is_file():
            raise ValidationError({"detail": "Родитель только папка"})
    return True


def _update_node(data: dict) -> FileSystem:
    node = FileSystem.objects.get(id=data["id"])
    old_size = node.size
    if data.get("size"):
        node.size = data["size"]
    node.date = data["date"]
    if data.get("url"):
        node.url = data["url"]
    node.save()
    if data.get("parent") and node.parent != data["parent"]:
        node.move_to(target=data["parent"], old_size=old_size)
    else:
        change_size_set_data(instance=node, old_size=old_size)
    return node


class UpdatesViewSet(mixins.ListModelMixin, GenericViewSet):
    def list(self, request, *args, **kwargs):
        date = request.query_params.get("date")
        if not date:
            raise ValidationError({"detail": "Отсутствует date"})

        request.data["date"] = date
        serializer = DateTimeSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            raise ValidationError({"detail": "Некорректная date"})

        end_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        one_day_delta = timedelta(hours=24)
        start_date = end_date - one_day_delta
        nodes = FileSystem.objects.filter(
            type=TYPE_FILE, date__range=(start_date, end_date)
        )
        serializer = NodesUpdateSerializer({"items": nodes})
        return Response(serializer.data)


class DeleteViewSet(mixins.DestroyModelMixin, GenericViewSet):
    def destroy(self, request, *args, **kwargs):
        new_date = request.query_params.get("date")
        if new_date:
            node = get_object_or_404(FileSystem, id=kwargs["pk"])
            request.data["date"] = new_date
            serializer = DateTimeSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                node.date = new_date
                node.save()
                recount_size_set_data(instance=node, add_operation=False)
                node.delete()
            return Response(status=status.HTTP_200_OK)
        raise ValidationError({"detail": "Некорректное значение"})


class HistoryViewSet(mixins.ListModelMixin, GenericViewSet):
    def list(self, request, *args, **kwargs):
        date_start = request.query_params.get("dateStart")
        date_end = request.query_params.get("dateEnd")
        if (date_start and not date_end) or (date_end and not date_start):
            raise ValidationError({"detail": "Некорректные интервалы"})

        node = get_object_or_404(FileSystem, id=kwargs["node_id"])
        query_without_dates = date_start is None and date_end is None
        if query_without_dates:
            positions = History.objects.filter(node=node).values_list(
                "position", flat=True
            )
        else:
            data = [{"date": date_start}, {"date": date_end}]
            serializer = DateTimeSerializer(data=data, many=True)
            if not serializer.is_valid(raise_exception=True):
                raise ValidationError({"detail": "Невалидные интервалы"})

            date_start = datetime.strptime(date_start, "%Y-%m-%dT%H:%M:%SZ")
            one_sec_delta = timedelta(seconds=1)
            date_end = (
                datetime.strptime(date_end, "%Y-%m-%dT%H:%M:%SZ")
                - one_sec_delta
            )

            positions = History.objects.filter(
                node=node, change_date__range=(date_start, date_end)
            ).values_list("position", flat=True)
        data = {"items": [eval(position) for position in positions]}
        return Response(data)
