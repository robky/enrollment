from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from core.models import FileSystem, TYPE_NAME


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
    id = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    parentId = serializers.CharField(required=False)
    size = serializers.IntegerField(min_value=1, required=False)

    class Meta:
        model = FileSystem
        fields = ("id", "url", "parentId", "size", "type")

    def validate_str_name_id(self, value):
        name = value.split('_')
        if (len(name) == 3 and name[0] == 'элемент' and name[1].isdigit() and name[2].isdigit()):
            return value
        raise serializers.ValidationError("Некорректный идентификатор")

    def validate_id(self, value):
        return self.validate_str_name_id(value)

    def validate_parentId(self, value):
        return self.validate_str_name_id(value)

    def validate_type(self, value):
        if value in TYPE_NAME:
            return value
        raise serializers.ValidationError("Некорректный тип")

    def validate(self, attrs):
        if attrs.get('type') == 'FILE':
            if 'url' not in attrs or 'size' not in attrs or 'parentId' not in attrs:
                raise serializers.ValidationError("Недостаточно данных")
        return attrs


class NodesImportsSerializer(serializers.Serializer):
    items = NodesItemsSerializer(many=True)
    updateDate = serializers.DateTimeField(required=True)

    class Meta:
        fields = ("items", "updateDate")
        extra_kwargs = {"updateDate": {
            "error_messages": {"required": "Give yourself a username"}}}

    def validate_items(self, value):
        if value:
            return value
        raise serializers.ValidationError("Пустое значение")
