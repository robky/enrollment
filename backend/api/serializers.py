from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from core.models import FileSystem


class NodesSerializer(serializers.ModelSerializer):
    id = serializers.StringRelatedField(source="get_name_str")
    type = serializers.CharField(source="get_type_display")
    parentId = serializers.CharField(source="parent")
    children = RecursiveField(many=True)

    class Meta:
        model = FileSystem
        fields = ("id", "url", "type", "parentId", "date", "size", "children")

    def to_representation(self, instance):
        result = super(NodesSerializer, self).to_representation(instance)
        if result.get("type") == "FILE":
            result.pop("children")
        return result


class NodesItemsSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    parentId = serializers.CharField()
    type = serializers.CharField()
    parentId = serializers.CharField()

    class Meta:
        model = FileSystem
        fields = ("id", "url", "parenId", "size", "type")


class NodesImportsSerializer(serializers.Serializer):
    items = NodesItemsSerializer(many=True)
    updateDate = serializers.CharField(source="get_type_display")

    class Meta:
        fields = ("items", "updateDate")
