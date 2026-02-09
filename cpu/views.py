from rest_framework import viewsets

from cpu.models import CpuComponent
from cpu.serializers import CpuComponentSerializer


class CpuComponentViewSet(viewsets.ModelViewSet):
    queryset = CpuComponent.objects.all()
    serializer_class = CpuComponentSerializer
    search_fields = ["name"]
    ordering_fields = ["created_at", "name", "cores", "clock_speed"]
