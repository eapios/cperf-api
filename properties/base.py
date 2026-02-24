from django.db import models


class BaseEntity(models.Model):
    """
    Abstract base — stamps name + timestamps onto every child.
    No DB table created. Pure code-level DRY shortcut.
    """

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name
