from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("cpu.urls")),
    path("api/", include("dram.urls")),
    path("api/", include("nand.urls")),
    path("api/", include("properties.urls")),
    path("api/", include("results.urls")),
    path("api-auth/", include("rest_framework.urls")),
]
