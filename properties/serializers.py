from rest_framework import serializers

from properties.models import (
    ExtendedProperty,
    ExtendedPropertySet,
    ExtendedPropertySetMembership,
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

class ExtendedPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedProperty
        fields = ["id", "content_type", "name", "is_formula", "default_value"]


# --- ExtendedPropertySetMembership (nested inside set) ---

class ExtendedPropertySetMembershipSerializer(serializers.ModelSerializer):
    extended_property = ExtendedPropertySerializer(read_only=True)
    extended_property_id = serializers.PrimaryKeyRelatedField(
        queryset=ExtendedProperty.objects.all(),
        source="extended_property",
        write_only=True,
    )
    property_set_id = serializers.PrimaryKeyRelatedField(
        queryset=ExtendedPropertySet.objects.all(),
        source="property_set",
        write_only=True,
    )

    class Meta:
        model = ExtendedPropertySetMembership
        fields = ["id", "index", "extended_property", "extended_property_id", "property_set_id"]


# --- ExtendedPropertySet ---

class ExtendedPropertySetSerializer(serializers.ModelSerializer):
    items = ExtendedPropertySetMembershipSerializer(
        source="memberships", many=True, read_only=True
    )

    class Meta:
        model = ExtendedPropertySet
        fields = ["id", "name", "content_type", "items"]


# --- ExtendedPropertyValue ---

class ExtendedPropertyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedPropertyValue
        fields = [
            "id", "extended_property", "content_type", "object_id", "value",
        ]
