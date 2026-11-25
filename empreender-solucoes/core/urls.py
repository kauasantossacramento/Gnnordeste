from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("a-empresa/", views.sobre, name="sobre"),
    path("servicos/", views.servicos, name="servicos"),
    path("servicos/<slug:slug>/", views.servico, name="servico"),
    path("monte-sua-equipe/", views.proposta, name="proposta"),
    path("carreiras/", views.carreiras, name="carreiras"),
    path("carreiras/acompanhar/", views.acompanhar, name="acompanhar"),
    path("carreiras/<slug:slug>/", views.vaga, name="vaga"),
    path("conteudos/", views.conteudos, name="conteudos"),
    path("conteudos/<slug:slug>/", views.artigo, name="artigo"),
    path("contato/", views.contato, name="contato"),
    path("p/<slug:slug>/", views.pagina, name="pagina"),
]
