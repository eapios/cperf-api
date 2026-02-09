from rest_framework.routers import DefaultRouter

from components.views import ComponentViewSet

router = DefaultRouter()
router.register("", ComponentViewSet, basename="component")

urlpatterns = router.urls
