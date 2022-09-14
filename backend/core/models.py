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

    def move_to(self, target, old_size: int):
        recount_size_set_data(instance=self, old_size=-old_size)
        super(FileSystem, self).move_to(target)
        recount_size_set_data(instance=self)

    def as_json(self):
        return dict(
            id=self.id,
            url=self.url,
            date=self.date.isoformat() + "Z",
            parentId=self.parent_id,
            size=self.size,
            type=self.get_type_display(),
        )


class History(models.Model):
    node = models.ForeignKey(
        FileSystem,
        on_delete=models.CASCADE,
        related_name="history",
    )
    change_date = models.DateTimeField()
    position = models.TextField()

    def __str__(self):
        return f"{self.node} - {self.change_date}"


def recount_size_set_data(
    instance: FileSystem, add_operation: bool = True, old_size: int = 0
):
    new_date = instance.date
    if old_size:
        new_size = old_size
    else:
        new_size = instance.size if add_operation else -instance.size
    with transaction.atomic():
        instance.get_ancestors().filter(type=TYPE_FOLDER).update(
            size=F("size") + new_size, date=new_date
        )


def change_size_set_data(instance: FileSystem, old_size: int):
    new_date = instance.date
    different_size = instance.size - old_size
    with transaction.atomic():
        instance.get_ancestors().filter(type=TYPE_FOLDER).update(
            size=F("size") + different_size, date=new_date
        )


def set_position_history(node: FileSystem):
    History.objects.create(
        node=node, change_date=node.date, position=node.as_json()
    )


def bulk_position_history(nodes: list):
    if nodes:
        data = [
            History(node=node, change_date=node.date, position=node.as_json())
            for node in nodes
        ]
        History.objects.bulk_create(data)


def print_latest_queries():
    for i in connection.queries:
        print("sql:", i["sql"])
        print("time:", i["time"])
        print()
    reset_queries()
