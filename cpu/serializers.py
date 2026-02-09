from decimal import Decimal

from rest_framework import serializers

from cpu.models import CpuComponent


class CpuComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CpuComponent
        fields = [
            "id",
            "name",
            "component_type",
            "description",
            "cores",
            "threads",
            "clock_speed",
            "boost_clock",
            "tdp",
            "socket",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "component_type", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Name must not be blank.")
        return value

    def validate(self, attrs: dict) -> dict:
        cores = attrs.get("cores", getattr(self.instance, "cores", None))
        threads = attrs.get("threads", getattr(self.instance, "threads", None))
        clock_speed = attrs.get(
            "clock_speed", getattr(self.instance, "clock_speed", None)
        )
        boost_clock = attrs.get(
            "boost_clock", getattr(self.instance, "boost_clock", None)
        )

        if cores is not None and threads is not None and threads < cores:
            raise serializers.ValidationError(
                {"threads": "Threads must be greater than or equal to cores."}
            )

        if (
            boost_clock is not None
            and clock_speed is not None
            and Decimal(str(boost_clock)) < Decimal(str(clock_speed))
        ):
            raise serializers.ValidationError(
                {"boost_clock": "Boost clock must be greater than or equal to base clock speed."}
            )

        return attrs
