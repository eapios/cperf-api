from django.db import models

from properties.base import BaseEntity


class Dram(BaseEntity):
    """DRAM component for performance calculation."""

    bandwidth = models.FloatField()
    channel = models.PositiveSmallIntegerField()
    transfer_rate = models.FloatField()

    class Meta:
        verbose_name = "DRAM"
        verbose_name_plural = "DRAMs"
