from django.contrib import admin

from results.models import (
    ResultProfile,
    ResultProfileWorkload,
    ResultRecord,
    ResultWorkload,
)


@admin.register(ResultProfile)
class ResultProfileAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(ResultWorkload)
class ResultWorkloadAdmin(admin.ModelAdmin):
    list_display = ["name", "type"]
    search_fields = ["name"]


@admin.register(ResultProfileWorkload)
class ResultProfileWorkloadAdmin(admin.ModelAdmin):
    list_display = ["profile", "workload", "config_set", "extended_property_set"]
    list_filter = ["profile"]


@admin.register(ResultRecord)
class ResultRecordAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]
