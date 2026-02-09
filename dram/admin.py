from django.contrib import admin

from dram.models import DramComponent


@admin.register(DramComponent)
class DramComponentAdmin(admin.ModelAdmin):
    list_display = ["name", "capacity_gb", "speed_mhz", "ddr_type", "modules", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "component_type", "created_at", "updated_at"]
