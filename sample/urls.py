from rest_framework.routers import DefaultRouter

from sample.views import SampleItemViewSet

router = DefaultRouter()
router.register("items", SampleItemViewSet)

urlpatterns = router.urls
