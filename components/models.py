import uuid

from django.db import models


class Component(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    component_type = models.CharField(max_length=50)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["component_type"], name="idx_component_type"),
            models.Index(fields=["created_at"], name="idx_component_created"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.component_type})"
