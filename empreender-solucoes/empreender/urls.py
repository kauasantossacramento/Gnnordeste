import os

from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.static import serve

from core.sitemaps import SITEMAPS
from core.views import robots_txt

urlpatterns = [
    path("painel/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", robots_txt),
    path("", include("core.urls")),
]

# Uploads do painel. Com Nginx/Apache servindo /media/, defina DJANGO_SERVE_MEDIA=false.
if settings.DEBUG or os.environ.get("DJANGO_SERVE_MEDIA", "true").lower() == "true":
    urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})]

handler404 = "core.views.erro_404"
