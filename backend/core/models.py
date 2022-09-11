from django.db import models, reset_queries, connection, transaction
from django.db.models import F

from mptt.models import MPTTModel, TreeForeignKey

TYPE_FOLDER = 1
TYPE_FILE = 2
TYPE_CHOICES = (
    (TYPE_FOLDER, 'FOLDER'),
    (TYPE_FILE, 'FILE'),
)


class FileSystem(MPTTModel):
    url = models.CharField(null=True, max_length=255, default=None)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    date = models.DateTimeField()
    size = models.IntegerField(default=0)

    def __str__(self):
        parent = self.parent_id if self.parent else self.id
        return f'элемент_{parent}_{self.id}'

    def save(self, *args, **kwargs):
        try:
            old_instance = FileSystem.objects.get(id=self.id)
        except FileSystem.DoesNotExist:
            super().save(*args, **kwargs)
            _recount_size(instance=self, value=self.size)
            return
        _recount_size(instance=self, value=self.size - old_instance.size)
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        _recount_size(instance=self, value=-self.size)
        return super().delete(*args, **kwargs)


def _recount_size(instance: FileSystem, value: int):
    with transaction.atomic():
        instance.get_ancestors().filter(type=1).update(size=F('size') + value)


def print_latest_queries():
    for i in connection.queries:
        print("sql:", i["sql"])
        print("time:", i["time"])
        print()
    reset_queries()
