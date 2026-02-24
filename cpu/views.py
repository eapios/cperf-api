from rest_framework import viewsets

from cpu.models import Cpu
from cpu.serializers import CpuSerializer


class CpuViewSet(viewsets.ModelViewSet):
    queryset = Cpu.objects.all()
    serializer_class = CpuSerializer
    search_fields = ["name"]
    ordering_fields = ["created_at", "name", "bandwidth"]
