from typing import Any

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from properties.models import ExtendedPropertyValue
from results.models import (
    ResultInstance,
    ResultProfile,
    ResultProfileWorkload,
    ResultRecord,
    ResultWorkload,
)


class ResultProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultProfile
        fields = ["id", "name"]


class ResultWorkloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultWorkload
        fields = ["id", "name", "type"]


class ResultProfileWorkloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultProfileWorkload
        fields = [
            "id", "profile", "workload", "config_set", "extended_property_set",
        ]


class ResultRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultRecord
        fields = [
            "id", "name",
            "nand", "nand_instance", "nand_perf", "cpu", "dram",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ResultInstanceSerializer(serializers.ModelSerializer):
    extended_properties = serializers.SerializerMethodField()

    class Meta:
        model = ResultInstance
        fields = [
            "id", "profile_workload", "result_record",
            "extended_properties",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_extended_properties(self, obj: ResultInstance) -> Any:
        request = self.context.get("request")
        if not request:
            return None
        include = request.query_params.get("include", "")
        if "extended_properties" not in include:
            return None
        ct = ContentType.objects.get_for_model(ResultInstance)
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
