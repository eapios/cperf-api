from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/components/", include("components.urls")),
    path("api/cpu/", include("cpu.urls")),
    path("api/dram/", include("dram.urls")),
    path("api-auth/", include("rest_framework.urls")),
]
