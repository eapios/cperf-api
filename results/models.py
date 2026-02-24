from django.db import models

from properties.base import BaseEntity
from properties.models import ExtendedPropertySet, PropertyConfigSet


class ResultProfile(models.Model):
    """A result grouping (e.g. AIPR Upper Bound, Multi-plane Read)."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Result Profiles"

    def __str__(self) -> str:
        return self.name


class ResultWorkload(models.Model):
    """A workload definition (e.g. Host Write, TLC Erase, GC Read)."""

    name = models.CharField(max_length=255)
    type = models.IntegerField(help_text="Workload type identifier (opaque integer)")

    profiles = models.ManyToManyField(
        ResultProfile,
        through="ResultProfileWorkload",
        related_name="workloads",
    )

    def __str__(self) -> str:
        return self.name


class ResultProfileWorkload(models.Model):
    """
    Through model: a workload's appearance in a specific profile.
    Each appearance carries its own config_set and extended_property_set.
    """

    profile = models.ForeignKey(
        ResultProfile, on_delete=models.CASCADE, related_name="profile_workloads"
    )
    workload = models.ForeignKey(
        ResultWorkload, on_delete=models.CASCADE, related_name="profile_workloads"
    )
    config_set = models.ForeignKey(
        PropertyConfigSet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_profile_workloads",
        help_text="Rendering config for this workload in this profile",
    )
    extended_property_set = models.ForeignKey(
        ExtendedPropertySet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_profile_workloads",
        help_text="Computed properties for this workload in this profile",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "workload"],
                name="unique_workload_per_profile",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.profile.name} / {self.workload.name}"


class ResultRecord(BaseEntity):
    """
    A saved result run — captures which hardware was selected.
    Hardware FKs are nullable; SET_NULL preserves the record on component deletion.
    """

    nand = models.ForeignKey(
        "nand.Nand",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_records",
    )
    nand_instance = models.ForeignKey(
        "nand.NandInstance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_records",
    )
    nand_perf = models.ForeignKey(
        "nand.NandPerf",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_records",
    )
    cpu = models.ForeignKey(
        "cpu.Cpu",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_records",
    )
    dram = models.ForeignKey(
        "dram.Dram",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="result_records",
    )

    class Meta:
        verbose_name = "Result Record"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class ResultInstance(models.Model):
    """
    A specific result entry — one per profile-workload per result record.
    Identified by (result_record, profile_workload) pair.
    """

    profile_workload = models.ForeignKey(
        ResultProfileWorkload,
        on_delete=models.CASCADE,
        related_name="instances",
    )
    result_record = models.ForeignKey(
        ResultRecord,
        on_delete=models.CASCADE,
        related_name="result_instances",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Result Instance"
        constraints = [
            models.UniqueConstraint(
                fields=["result_record", "profile_workload"],
                name="unique_result_per_record_workload",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.result_record.name} / {self.profile_workload}"
