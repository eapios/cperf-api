from rest_framework import serializers

from results.models import (
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
        fields = ["id", "name", "data", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
