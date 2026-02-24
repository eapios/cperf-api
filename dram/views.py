from rest_framework import viewsets

from dram.models import Dram
from dram.serializers import DramSerializer


class DramViewSet(viewsets.ModelViewSet):
    queryset = Dram.objects.all()
    serializer_class = DramSerializer
    search_fields = ["name"]
    ordering_fields = ["created_at", "name", "bandwidth"]
