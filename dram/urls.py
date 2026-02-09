from rest_framework.routers import DefaultRouter

from dram.views import DramComponentViewSet

router = DefaultRouter()
router.register("", DramComponentViewSet, basename="dram")

urlpatterns = router.urls
