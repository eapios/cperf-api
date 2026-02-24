import django_filters
from rest_framework import viewsets

from results.models import (
    ResultInstance,
    ResultProfile,
    ResultProfileWorkload,
    ResultRecord,
    ResultWorkload,
)
from results.serializers import (
    ResultInstanceSerializer,
    ResultProfileSerializer,
    ResultProfileWorkloadSerializer,
    ResultRecordSerializer,
    ResultWorkloadSerializer,
)


class ResultProfileViewSet(viewsets.ModelViewSet):
    queryset = ResultProfile.objects.all()
    serializer_class = ResultProfileSerializer
    search_fields = ["name"]
    ordering_fields = ["name"]


class ResultWorkloadViewSet(viewsets.ModelViewSet):
    queryset = ResultWorkload.objects.all()
    serializer_class = ResultWorkloadSerializer
    search_fields = ["name"]
    ordering_fields = ["name", "type"]


class ResultProfileWorkloadFilter(django_filters.FilterSet):
    profile = django_filters.NumberFilter(field_name="profile")

    class Meta:
        model = ResultProfileWorkload
        fields = ["profile"]


class ResultProfileWorkloadViewSet(viewsets.ModelViewSet):
    queryset = ResultProfileWorkload.objects.select_related("profile", "workload").all()
    serializer_class = ResultProfileWorkloadSerializer
    filterset_class = ResultProfileWorkloadFilter


class ResultRecordViewSet(viewsets.ModelViewSet):
    queryset = ResultRecord.objects.all()
    serializer_class = ResultRecordSerializer
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]
    http_method_names = ["get", "post", "delete", "head", "options"]


class ResultInstanceFilter(django_filters.FilterSet):
    result_record = django_filters.NumberFilter(field_name="result_record")

    class Meta:
        model = ResultInstance
        fields = ["result_record"]


class ResultInstanceViewSet(viewsets.ModelViewSet):
    queryset = ResultInstance.objects.all()
    serializer_class = ResultInstanceSerializer
    filterset_class = ResultInstanceFilter
    http_method_names = ["get", "post", "delete", "head", "options"]
