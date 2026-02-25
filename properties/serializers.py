from rest_framework import serializers

from properties.models import (
    ExtendedProperty,
    ExtendedPropertySet,
    ExtendedPropertyValue,
    PropertyConfig,
    PropertyConfigSet,
    PropertyConfigSetMembership,
)


# --- PropertyConfig ---

class PropertyConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyConfig
        fields = [
            "id", "content_type", "name", "display_text", "description",
            "read_only", "is_extended", "is_primary", "is_numeric",
            "sub_type", "decimal_place", "unit",
        ]


# --- PropertyConfigSetMembership (nested inside set) ---

class PropertyConfigSetMembershipSerializer(serializers.ModelSerializer):
    config = PropertyConfigSerializer(read_only=True)
    config_id = serializers.PrimaryKeyRelatedField(
        queryset=PropertyConfig.objects.all(), source="config", write_only=True
    )

    class Meta:
        model = PropertyConfigSetMembership
        fields = ["id", "index", "config", "config_id"]


# --- PropertyConfigSet ---

class PropertyConfigSetSerializer(serializers.ModelSerializer):
    items = PropertyConfigSetMembershipSerializer(
        source="memberships", many=True, read_only=True
    )

    class Meta:
        model = PropertyConfigSet
        fields = ["id", "content_type", "name", "items"]


# --- ExtendedPropertySet ---

class ExtendedPropertySetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedPropertySet
        fields = ["id", "name", "content_type"]


# --- ExtendedProperty ---

class ExtendedPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedProperty
        fields = ["id", "content_type", "property_set", "name", "is_formula", "default_value"]

    def validate(self, attrs: dict) -> dict:
        ct = attrs.get("content_type", getattr(self.instance, "content_type", None))
        ps = attrs.get("property_set", getattr(self.instance, "property_set", None))
        if bool(ct) == bool(ps):
            raise serializers.ValidationError(
                "Exactly one of content_type or property_set must be set."
            )
        return attrs


# --- ExtendedPropertyValue ---

class ExtendedPropertyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedPropertyValue
        fields = [
            "id", "extended_property", "content_type", "object_id", "value",
        ]
