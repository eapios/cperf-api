from rest_framework.routers import DefaultRouter

from cpu.views import CpuComponentViewSet

router = DefaultRouter()
router.register("", CpuComponentViewSet, basename="cpu")

urlpatterns = router.urls
