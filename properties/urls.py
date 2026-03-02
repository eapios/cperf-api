from rest_framework.routers import DefaultRouter

from properties.views import (
    ExtendedPropertySetMembershipViewSet,
    ExtendedPropertySetViewSet,
    ExtendedPropertyValueViewSet,
    ExtendedPropertyViewSet,
    PropertyConfigSetViewSet,
    PropertyConfigViewSet,
)

router = DefaultRouter()
router.register("property-configs", PropertyConfigViewSet, basename="property-config")
router.register("config-sets", PropertyConfigSetViewSet, basename="config-set")
router.register("extended-property-sets", ExtendedPropertySetViewSet, basename="extended-property-set")
router.register("extended-properties", ExtendedPropertyViewSet, basename="extended-property")
router.register("extended-property-values", ExtendedPropertyValueViewSet, basename="extended-property-value")
router.register("extended-property-set-memberships", ExtendedPropertySetMembershipViewSet, basename="extended-property-set-membership")

urlpatterns = router.urls
