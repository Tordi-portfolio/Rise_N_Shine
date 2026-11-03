from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Rise 'N Shine Maid Services"
admin.site.site_title = "Rise 'N Shine admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]
