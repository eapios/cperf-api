from django.db import models

from properties.base import BaseEntity


class Cpu(BaseEntity):
    """CPU component for performance calculation."""

    bandwidth = models.FloatField()

    class Meta:
        verbose_name = "CPU"
        verbose_name_plural = "CPUs"
