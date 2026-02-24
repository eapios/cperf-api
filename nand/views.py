import django_filters
from rest_framework import viewsets

from nand.models import Nand, NandInstance, NandPerf
from nand.serializers import NandInstanceSerializer, NandPerfSerializer, NandSerializer, NandWriteSerializer


class NandFilter(django_filters.FilterSet):
    class Meta:
        model = Nand
        fields: list = []


class NandViewSet(viewsets.ModelViewSet):
    queryset = Nand.objects.all()
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT", "PATCH"):
            return NandWriteSerializer
        return NandSerializer


class NandInstanceFilter(django_filters.FilterSet):
    nand = django_filters.NumberFilter(field_name="nand")

    class Meta:
        model = NandInstance
        fields = ["nand"]


class NandInstanceViewSet(viewsets.ModelViewSet):
    queryset = NandInstance.objects.all()
    serializer_class = NandInstanceSerializer
    filterset_class = NandInstanceFilter
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]


class NandPerfFilter(django_filters.FilterSet):
    nand = django_filters.NumberFilter(field_name="nand")

    class Meta:
        model = NandPerf
        fields = ["nand"]


class NandPerfViewSet(viewsets.ModelViewSet):
    queryset = NandPerf.objects.all()
    serializer_class = NandPerfSerializer
    filterset_class = NandPerfFilter
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]
