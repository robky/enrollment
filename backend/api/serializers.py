from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from core.models import TYPE_NAME, FileSystem


class NodesSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="get_type_display")
    parentId = serializers.CharField(source="parent")
    children = RecursiveField(many=True)

    class Meta:
        model = FileSystem
        fields = ("id", "url", "type", "parentId", "date", "size", "children")

    def to_representation(self, instance):
        result = super(NodesSerializer, self).to_representation(instance)
        if result.get("type") == "FILE":
            result["children"] = None
        return result


class NodesItemsBaseSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=True)
    parentId = serializers.CharField(required=False, allow_null=True)
    size = serializers.IntegerField(min_value=1, required=False)

    def validate_type(self, value):
        if value in TYPE_NAME:
            return value
        raise serializers.ValidationError("Некорректный тип")

    def validate(self, attrs):
        if attrs.get("type") == "FILE":
            if (
                "url" not in attrs
                or "size" not in attrs
                or "parentId" not in attrs
            ):
                raise serializers.ValidationError("Недостаточно данных")
        return attrs


class NodesItemsImportSerializer(NodesItemsBaseSerializer):
    class Meta:
        model = FileSystem
        fields = ("id", "url", "parentId", "size", "type")


class NodesImportsSerializer(serializers.Serializer):
    items = NodesItemsImportSerializer(many=True)
    updateDate = serializers.DateTimeField(required=True)

    class Meta:
        fields = ("items", "updateDate")

    def validate_items(self, value):
        if value:
            return value
        raise serializers.ValidationError("Пустое значение")


class NodesItemsUpdateSerializer(NodesItemsBaseSerializer):
    type = serializers.CharField(source="get_type_display")
    parentId = serializers.CharField(allow_null=True)

    class Meta:
        model = FileSystem
        fields = ("id", "url", "date", "parentId", "size", "type")


class NodesUpdateSerializer(serializers.Serializer):
    items = NodesItemsUpdateSerializer(many=True)

    class Meta:
        fields = ("items",)


class DateTimeSerializer(serializers.Serializer):
    date = serializers.DateTimeField(required=True)
