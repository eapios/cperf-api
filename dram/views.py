from rest_framework import viewsets

from dram.models import DramComponent
from dram.serializers import DramComponentSerializer


class DramComponentViewSet(viewsets.ModelViewSet):
    queryset = DramComponent.objects.all()
    serializer_class = DramComponentSerializer
    search_fields = ["name"]
    ordering_fields = ["created_at", "name", "capacity_gb", "speed_mhz"]
