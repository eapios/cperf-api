from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class PropertyConfig(models.Model):
    """
    Rendering/display config for a property column.
    Bound to a model type via ContentType.
    """

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="property_configs",
        help_text="Which model type this config belongs to (Nand, Cpu, etc.)",
    )
    name = models.CharField(max_length=255)
    display_text = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    read_only = models.BooleanField(default=False)
    is_extended = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    is_numeric = models.BooleanField(default=False)
    sub_type = models.CharField(
        max_length=50, blank=True, default="", help_text="percent, byte, etc."
    )
    decimal_place = models.PositiveSmallIntegerField(null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ["content_type", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "name"],
                name="unique_config_per_model_type",
            ),
        ]

    def __str__(self) -> str:
        return self.display_text or self.name


class PropertyConfigSet(models.Model):
    """
    A named collection of PropertyConfigs for a specific model type.
    Multiple sets can exist per model type.
    """

    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="config_sets",
        help_text="Which model type this set is for (Nand, Cpu, etc.)",
    )
    configs = models.ManyToManyField(
        PropertyConfig,
        through="PropertyConfigSetMembership",
        related_name="config_sets",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "name"],
                name="unique_config_set_per_model_type",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class PropertyConfigSetMembership(models.Model):
    """
    Through model for PropertyConfigSet ↔ PropertyConfig M2M.
    Stores the display order (index) of a config within a specific set.
    """

    config_set = models.ForeignKey(
        PropertyConfigSet, on_delete=models.CASCADE, related_name="memberships"
    )
    config = models.ForeignKey(
        PropertyConfig, on_delete=models.CASCADE, related_name="memberships"
    )
    index = models.PositiveIntegerField(
        help_text="Display order of this config within the set"
    )

    class Meta:
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(
                fields=["config_set", "config"],
                name="unique_config_in_set",
            ),
            models.UniqueConstraint(
                fields=["config_set", "index"],
                name="unique_index_in_set",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.config_set.name}[{self.index}] = {self.config.name}"


class ExtendedPropertySet(models.Model):
    """
    A named collection of ExtendedProperties.
    content_type is optional — used to scope the set to a specific model type.
    """

    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="extended_property_sets",
        help_text="Model type for the set (e.g. ResultWorkload). Null for generic sets.",
    )

    def __str__(self) -> str:
        return self.name


class ExtendedProperty(models.Model):
    """
    Definition of a user-defined computed/constant property.

    Always bound to a content_type (required). Belongs to zero or more
    ExtendedPropertySets via ExtendedPropertySetMembership.

    Use only for static or formula-based values (e.g. formulas, fixed constants,
    default values). For properties that differ per hardware instance, add a
    native model field to the relevant Django model instead.
    """

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="extended_properties",
        help_text="Model type this property is bound to (e.g. Nand, Cpu, ResultWorkload).",
    )
    name = models.CharField(max_length=255)
    is_formula = models.BooleanField(default=False)
    default_value = models.JSONField(
        null=True,
        blank=True,
        default=None,
        help_text="Fallback value for instances with no per-instance value record",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "name"],
                name="unique_extended_prop_per_model_type",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class ExtendedPropertySetMembership(models.Model):
    """
    Through model for ExtendedPropertySet ↔ ExtendedProperty M2M.
    Stores the display order (index) of a property within a specific set.
    """

    property_set = models.ForeignKey(
        ExtendedPropertySet, on_delete=models.CASCADE, related_name="memberships"
    )
    extended_property = models.ForeignKey(
        ExtendedProperty, on_delete=models.CASCADE, related_name="memberships"
    )
    index = models.PositiveIntegerField(
        help_text="Display order of this property within the set"
    )

    class Meta:
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(
                fields=["property_set", "extended_property"],
                name="unique_extended_prop_in_set",
            ),
            models.UniqueConstraint(
                fields=["property_set", "index"],
                name="unique_index_in_extended_set",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.property_set.name}[{self.index}] = {self.extended_property.name}"


class ExtendedPropertyValue(models.Model):
    """
    Per-instance value for an ExtendedProperty.
    Uses GenericFK to point to any entity instance.
    """

    extended_property = models.ForeignKey(
        ExtendedProperty,
        on_delete=models.CASCADE,
        related_name="values",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="extended_property_values",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    value = models.JSONField(
        help_text="Formula string (when is_formula=True) or literal value"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["extended_property", "content_type", "object_id"],
                name="unique_value_per_prop_per_instance",
            ),
        ]
        indexes = [
            models.Index(
                fields=["content_type", "object_id"],
                name="idx_ext_prop_value_instance",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.extended_property.name} = {self.value}"
