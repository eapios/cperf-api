from django.contrib import admin

from cpu.models import Cpu


@admin.register(Cpu)
class CpuAdmin(admin.ModelAdmin):
    list_display = ["name", "bandwidth", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]
