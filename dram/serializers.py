from rest_framework import serializers

from dram.models import DramComponent


class DramComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DramComponent
        fields = [
            "id",
            "name",
            "component_type",
            "description",
            "capacity_gb",
            "speed_mhz",
            "ddr_type",
            "modules",
            "cas_latency",
            "voltage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "component_type", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Name must not be blank.")
        return value
