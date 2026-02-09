from django.contrib import admin

from sample.models import SampleItem


@admin.register(SampleItem)
class SampleItemAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "updated_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]
