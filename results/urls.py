from rest_framework.routers import DefaultRouter

from results.views import (
    ResultInstanceViewSet,
    ResultProfileViewSet,
    ResultProfileWorkloadViewSet,
    ResultRecordViewSet,
    ResultWorkloadViewSet,
)

router = DefaultRouter()
router.register("result-profiles", ResultProfileViewSet, basename="result-profile")
router.register("result-workloads", ResultWorkloadViewSet, basename="result-workload")
router.register("result-profile-workloads", ResultProfileWorkloadViewSet, basename="result-profile-workload")
router.register("result-records", ResultRecordViewSet, basename="result-record")
router.register("result-instances", ResultInstanceViewSet, basename="result-instance")

urlpatterns = router.urls
