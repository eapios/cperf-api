from rest_framework.routers import DefaultRouter

from nand.views import NandInstanceViewSet, NandPerfViewSet, NandViewSet

router = DefaultRouter()
router.register("nand", NandViewSet, basename="nand")
router.register("nand-instances", NandInstanceViewSet, basename="nand-instance")
router.register("nand-perf", NandPerfViewSet, basename="nand-perf")

urlpatterns = router.urls
