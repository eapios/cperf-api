from typing import Any

from django.db import models

from components.models import Component


class CpuComponent(Component):
    cores = models.PositiveIntegerField()
    threads = models.PositiveIntegerField()
    clock_speed = models.DecimalField(max_digits=5, decimal_places=2)
    boost_clock = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    tdp = models.PositiveIntegerField(null=True, blank=True)
    socket = models.CharField(max_length=50, blank=True, default="")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.component_type = "cpu"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "CPU Component"
        verbose_name_plural = "CPU Components"
