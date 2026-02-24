from django.contrib import admin

from dram.models import Dram


@admin.register(Dram)
class DramAdmin(admin.ModelAdmin):
    list_display = ["name", "bandwidth", "channel", "transfer_rate", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]
