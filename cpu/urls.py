from rest_framework.routers import DefaultRouter

from cpu.views import CpuViewSet

router = DefaultRouter()
router.register("cpu", CpuViewSet, basename="cpu")

urlpatterns = router.urls
