from django.contrib import admin

from cpu.models import CpuComponent


@admin.register(CpuComponent)
class CpuComponentAdmin(admin.ModelAdmin):
    list_display = ["name", "cores", "threads", "clock_speed", "socket", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "component_type", "created_at", "updated_at"]
