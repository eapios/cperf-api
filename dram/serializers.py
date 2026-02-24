from typing import Any

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from dram.models import Dram
from properties.models import ExtendedPropertyValue, PropertyConfigSet


class DramSerializer(serializers.ModelSerializer):
    config_set = serializers.SerializerMethodField()
    extended_properties = serializers.SerializerMethodField()

    class Meta:
        model = Dram
        fields = [
            "id", "name", "bandwidth", "channel", "transfer_rate",
            "config_set", "extended_properties",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_config_set(self, obj: Dram) -> Any:
        request = self.context.get("request")
        if not request:
            return None
        config_set_id = request.query_params.get("config_set")
        if not config_set_id:
            return None
        try:
            cs = PropertyConfigSet.objects.prefetch_related(
                "memberships__config"
            ).get(pk=config_set_id)
        except PropertyConfigSet.DoesNotExist:
            return None
        memberships = cs.memberships.select_related("config").order_by("index")
        return {
            "id": cs.id,
            "name": cs.name,
            "items": [
                {
                    "index": m.index,
                    "config": {
                        "id": m.config.id,
                        "name": m.config.name,
                        "display_text": m.config.display_text,
                        "unit": m.config.unit,
                        "decimal_place": m.config.decimal_place,
                        "is_numeric": m.config.is_numeric,
                    },
                }
                for m in memberships
            ],
        }

    def get_extended_properties(self, obj: Dram) -> Any:
        request = self.context.get("request")
        if not request:
            return None
        include = request.query_params.get("include", "")
        if "extended_properties" not in include:
            return None
        ct = ContentType.objects.get_for_model(Dram)
        values = ExtendedPropertyValue.objects.filter(
            content_type=ct, object_id=obj.pk
        ).select_related("extended_property")
        return [
            {
                "id": v.id,
                "property_id": v.extended_property_id,
                "name": v.extended_property.name,
                "is_formula": v.extended_property.is_formula,
                "value": v.value,
            }
            for v in values
        ]
