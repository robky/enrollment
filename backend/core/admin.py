from django.contrib import admin
from django.contrib.auth.models import Group, User
from mptt.admin import DraggableMPTTAdmin

from core.models import FileSystem


@admin.register(FileSystem)
class FileSystemAdmin(DraggableMPTTAdmin):
    empty_value_display = "null"
    list_display = ("indented_title", "url", "type", "date", "size")


admin.site.unregister(User)
admin.site.unregister(Group)
