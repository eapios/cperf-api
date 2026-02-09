from typing import Any

from django.db import models

from components.models import Component


class DramComponent(Component):
    capacity_gb = models.PositiveIntegerField()
    speed_mhz = models.PositiveIntegerField()
    ddr_type = models.CharField(max_length=10)
    modules = models.PositiveIntegerField(default=1)
    cas_latency = models.PositiveIntegerField(null=True, blank=True)
    voltage = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.component_type = "dram"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "DRAM Component"
        verbose_name_plural = "DRAM Components"
