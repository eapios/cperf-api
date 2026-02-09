from rest_framework import mixins, viewsets

from components.models import Component
from components.serializers import ComponentSerializer


class ComponentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    filterset_fields = ["component_type"]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]
