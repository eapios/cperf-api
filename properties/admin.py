from django.contrib import admin

from properties.models import (
    ExtendedProperty,
    ExtendedPropertySet,
    ExtendedPropertyValue,
    PropertyConfig,
    PropertyConfigSet,
    PropertyConfigSetMembership,
)


@admin.register(PropertyConfig)
class PropertyConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "content_type", "display_text", "is_numeric", "unit"]
    list_filter = ["content_type"]
    search_fields = ["name", "display_text"]


@admin.register(PropertyConfigSet)
class PropertyConfigSetAdmin(admin.ModelAdmin):
    list_display = ["name", "content_type"]
    list_filter = ["content_type"]
    search_fields = ["name"]


@admin.register(PropertyConfigSetMembership)
class PropertyConfigSetMembershipAdmin(admin.ModelAdmin):
    list_display = ["config_set", "config", "index"]
    list_filter = ["config_set"]


@admin.register(ExtendedPropertySet)
class ExtendedPropertySetAdmin(admin.ModelAdmin):
    list_display = ["name", "content_type"]
    list_filter = ["content_type"]
    search_fields = ["name"]


@admin.register(ExtendedProperty)
class ExtendedPropertyAdmin(admin.ModelAdmin):
    list_display = ["name", "content_type", "property_set", "is_formula"]
    list_filter = ["content_type", "property_set", "is_formula"]
    search_fields = ["name"]


@admin.register(ExtendedPropertyValue)
class ExtendedPropertyValueAdmin(admin.ModelAdmin):
    list_display = ["extended_property", "content_type", "object_id", "value"]
    list_filter = ["content_type"]
