from django.core.validators import MinValueValidator
from django.db import models

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
    size = models.IntegerField(
        null=True, validators=[MinValueValidator(1)], default=None)

    def __str__(self):
        parent = self.parent_id if self.parent else self.id
        return f'элемент_{parent}_{self.id}'
