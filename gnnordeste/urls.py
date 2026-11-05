import os

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

admin.site.site_header = "Grupo Nordeste — Painel"
admin.site.site_title = "Grupo Nordeste"
admin.site.index_title = "Gerenciar conteúdo do site"

urlpatterns = [
    path("painel/", admin.site.urls),
    path("", include("core.urls")),
]

# Arquivos enviados pelo painel (imagens, PDFs). Em servidores com Nginx/Apache,
# prefira servir /media/ direto e defina DJANGO_SERVE_MEDIA=false.
if settings.DEBUG or os.environ.get("DJANGO_SERVE_MEDIA", "true").lower() == "true":
    urlpatterns += [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})]

handler404 = "core.views.erro_404"
