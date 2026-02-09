from rest_framework.viewsets import ModelViewSet

from sample.models import SampleItem
from sample.serializers import SampleItemSerializer


class SampleItemViewSet(ModelViewSet):
    queryset = SampleItem.objects.all()
    serializer_class = SampleItemSerializer
    ordering_fields = ["name", "created_at"]
    search_fields = ["name"]
