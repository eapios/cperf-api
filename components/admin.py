from django.contrib import admin

from components.models import Component


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ["name", "component_type", "created_at"]
    list_filter = ["component_type"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]
