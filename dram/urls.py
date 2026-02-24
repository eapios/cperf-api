from rest_framework.routers import DefaultRouter

from dram.views import DramViewSet

router = DefaultRouter()
router.register("dram", DramViewSet, basename="dram")

urlpatterns = router.urls
