import django_filters
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from properties.models import (
    ExtendedProperty,
    ExtendedPropertySet,
    ExtendedPropertySetMembership,
    ExtendedPropertyValue,
    PropertyConfig,
    PropertyConfigSet,
)
from properties.serializers import (
    ExtendedPropertySerializer,
    ExtendedPropertySetMembershipSerializer,
    ExtendedPropertySetSerializer,
    ExtendedPropertyValueSerializer,
    PropertyConfigSerializer,
    PropertyConfigSetSerializer,
)


class ModelTypeFilter(django_filters.FilterSet):
    """Filter by model app_label via ?model=<app_label>."""
    model = django_filters.CharFilter(method="filter_by_model")

    def filter_by_model(self, queryset, name, value):
        try:
            ct = ContentType.objects.get(app_label=value)
            return queryset.filter(content_type=ct)
        except ContentType.DoesNotExist:
            return queryset.none()


class PropertyConfigFilter(ModelTypeFilter):
    class Meta:
        model = PropertyConfig
        fields: list = []


class PropertyConfigViewSet(viewsets.ModelViewSet):
    queryset = PropertyConfig.objects.select_related("content_type").all()
    serializer_class = PropertyConfigSerializer
    filterset_class = PropertyConfigFilter
    search_fields = ["name", "display_text"]
    ordering_fields = ["name"]


class PropertyConfigSetFilter(ModelTypeFilter):
    class Meta:
        model = PropertyConfigSet
        fields: list = []


class PropertyConfigSetViewSet(viewsets.ModelViewSet):
    queryset = PropertyConfigSet.objects.select_related("content_type").prefetch_related(
        "memberships__config"
    ).all()
    serializer_class = PropertyConfigSetSerializer
    filterset_class = PropertyConfigSetFilter
    search_fields = ["name"]


class ExtendedPropertySetFilter(ModelTypeFilter):
    class Meta:
        model = ExtendedPropertySet
        fields: list = []


class ExtendedPropertySetViewSet(viewsets.ModelViewSet):
    queryset = ExtendedPropertySet.objects.select_related("content_type").prefetch_related(
        "memberships__extended_property"
    ).all()
    serializer_class = ExtendedPropertySetSerializer
    filterset_class = ExtendedPropertySetFilter
    search_fields = ["name"]


class ExtendedPropertyFilter(django_filters.FilterSet):
    model = django_filters.CharFilter(method="filter_by_model")
    set = django_filters.NumberFilter(method="filter_by_set")

    def filter_by_model(self, queryset, name, value):
        try:
            ct = ContentType.objects.get(app_label=value)
            return queryset.filter(content_type=ct)
        except ContentType.DoesNotExist:
            return queryset.none()

    def filter_by_set(self, queryset, name, value):
        return queryset.filter(memberships__property_set_id=value)

    class Meta:
        model = ExtendedProperty
        fields: list = []


class ExtendedPropertyViewSet(viewsets.ModelViewSet):
    queryset = ExtendedProperty.objects.all()
    serializer_class = ExtendedPropertySerializer
    filterset_class = ExtendedPropertyFilter
    search_fields = ["name"]

    @action(detail=True, methods=["get"], url_path="resolve")
    def resolve(self, request, pk: int = None) -> Response:
        # Bypass filterset (it intercepts 'model' query param) — look up directly.
        prop = get_object_or_404(ExtendedProperty, pk=pk)
        model = request.query_params.get("model")
        object_id = request.query_params.get("object_id")
        if not model or not object_id:
            return Response(
                {"detail": "'model' and 'object_id' query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model_name = request.query_params.get("model_name")
        try:
            if model_name:
                ct = ContentType.objects.get(app_label=model, model=model_name)
            else:
                ct = ContentType.objects.get(app_label=model)
        except ContentType.DoesNotExist:
            return Response({"detail": "Unknown model."}, status=status.HTTP_404_NOT_FOUND)
        except ContentType.MultipleObjectsReturned:
            return Response(
                {"detail": "'model' matches multiple models; provide 'model_name' to disambiguate."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            val = prop.values.get(content_type=ct, object_id=int(object_id)).value
            is_default = False
        except ExtendedPropertyValue.DoesNotExist:
            val = prop.default_value
            is_default = True
        return Response({"property_id": prop.pk, "value": val, "is_default": is_default})


class ExtendedPropertyValueFilter(django_filters.FilterSet):
    model = django_filters.CharFilter(method="filter_by_model")
    object_id = django_filters.NumberFilter(field_name="object_id")

    def filter_by_model(self, queryset, name, value):
        try:
            ct = ContentType.objects.get(app_label=value)
            return queryset.filter(content_type=ct)
        except ContentType.DoesNotExist:
            return queryset.none()

    class Meta:
        model = ExtendedPropertyValue
        fields: list = []


class ExtendedPropertyValueViewSet(viewsets.ModelViewSet):
    queryset = ExtendedPropertyValue.objects.select_related("extended_property").all()
    serializer_class = ExtendedPropertyValueSerializer
    filterset_class = ExtendedPropertyValueFilter


class ExtendedPropertySetMembershipViewSet(viewsets.ModelViewSet):
    queryset = ExtendedPropertySetMembership.objects.select_related(
        "property_set", "extended_property"
    ).all()
    serializer_class = ExtendedPropertySetMembershipSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]
