from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("quem-somos/", views.quem_somos, name="quem_somos"),
    path("unidades/", views.unidades, name="unidades"),
    path("unidades/<slug:slug>/", views.unidade, name="unidade"),
    path("trabalhe-conosco/", views.trabalhe, name="trabalhe"),
    path("trabalhe-conosco/<slug:slug>/", views.vaga, name="vaga"),
    path("noticias/", views.noticias, name="noticias"),
    path("noticias/<slug:slug>/", views.noticia, name="noticia"),
    path("contato/", views.contato, name="contato"),
    path("canal-de-denuncias/", views.denuncias, name="denuncias"),
]
