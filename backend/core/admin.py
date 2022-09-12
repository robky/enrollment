from django.contrib import admin
from django.contrib.auth.models import Group, User
from mptt.admin import DraggableMPTTAdmin

from core.models import FileSystem


@admin.register(FileSystem)
class FileSystemAdmin(DraggableMPTTAdmin):
    empty_value_display = "null"
    list_display = ("indented_title", "url", "type", "date", "size")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(User)
admin.site.unregister(Group)
