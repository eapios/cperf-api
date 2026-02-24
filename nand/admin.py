from django.contrib import admin

from nand.models import Nand, NandInstance, NandPerf


@admin.register(Nand)
class NandAdmin(admin.ModelAdmin):
    list_display = ["name", "capacity_per_die", "plane_per_die", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(NandInstance)
class NandInstanceAdmin(admin.ModelAdmin):
    list_display = ["name", "nand", "module_capacity", "user_capacity", "created_at"]
    search_fields = ["name"]
    list_filter = ["nand"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(NandPerf)
class NandPerfAdmin(admin.ModelAdmin):
    list_display = ["name", "nand", "bandwidth", "channel", "die_per_channel", "created_at"]
    search_fields = ["name"]
    list_filter = ["nand"]
    readonly_fields = ["id", "created_at", "updated_at"]
