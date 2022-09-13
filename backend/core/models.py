from django.db import connection, models, reset_queries, transaction
from django.db.models import F
from mptt.models import MPTTModel, TreeForeignKey

TYPE_FOLDER = 1
TYPE_FILE = 2
TYPE_CHOICES = (
    (TYPE_FOLDER, "FOLDER"),
    (TYPE_FILE, "FILE"),
)
TYPE_NAME = dict(reversed(item) for item in TYPE_CHOICES)


class FileSystem(MPTTModel):
    id = models.CharField(primary_key=True, unique=True, max_length=50)
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
        return self.id

    def move_to(self, target):
        old_instance = FileSystem.objects.get(id=self.id)
        recount_size_set_data(instance=old_instance, add_operation=False)
        super(FileSystem, self).move_to(target)
        recount_size_set_data(instance=self)


def recount_size_set_data(instance: FileSystem, add_operation: bool = True):
    new_date = instance.date
    new_size = instance.size if add_operation else -instance.size
    with transaction.atomic():
        instance.get_ancestors().filter(type=TYPE_FOLDER).update(
            size=F("size") + new_size, date=new_date
        )


def print_latest_queries():
    for i in connection.queries:
        print("sql:", i["sql"])
        print("time:", i["time"])
        print()
    reset_queries()
