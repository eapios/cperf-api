import django_filters
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets

from properties.models import (
    ExtendedProperty,
    ExtendedPropertySet,
    ExtendedPropertyValue,
    PropertyConfig,
    PropertyConfigSet,
)
from properties.serializers import (
    ExtendedPropertySerializer,
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
    queryset = ExtendedPropertySet.objects.all()
    serializer_class = ExtendedPropertySetSerializer
    filterset_class = ExtendedPropertySetFilter
    search_fields = ["name"]


class ExtendedPropertyFilter(django_filters.FilterSet):
    model = django_filters.CharFilter(method="filter_by_model")
    property_set = django_filters.NumberFilter(field_name="property_set")

    def filter_by_model(self, queryset, name, value):
        try:
            ct = ContentType.objects.get(app_label=value)
            return queryset.filter(content_type=ct)
        except ContentType.DoesNotExist:
            return queryset.none()

    class Meta:
        model = ExtendedProperty
        fields: list = []


class ExtendedPropertyViewSet(viewsets.ModelViewSet):
    queryset = ExtendedProperty.objects.all()
    serializer_class = ExtendedPropertySerializer
    filterset_class = ExtendedPropertyFilter
    search_fields = ["name"]


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
