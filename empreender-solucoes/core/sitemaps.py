from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Artigo, Pagina, Servico, Vaga


class Estaticas(Sitemap):
    changefreq = "weekly"

    def items(self):
        return ["core:home", "core:sobre", "core:servicos", "core:proposta", "core:carreiras",
                "core:conteudos", "core:contato"]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == "core:home" else 0.8


class Servicos(Sitemap):
    priority = 0.8

    def items(self):
        return Servico.objects.filter(ativo=True)


class Vagas(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Vaga.abertas()

    def lastmod(self, obj):
        return obj.atualizado_em


class Artigos(Sitemap):
    priority = 0.6

    def items(self):
        return Artigo.objects.filter(publicado=True)

    def lastmod(self, obj):
        return obj.data


class Paginas(Sitemap):
    priority = 0.3

    def items(self):
        return Pagina.objects.filter(publicado=True)

    def lastmod(self, obj):
        return obj.atualizado_em


SITEMAPS = {"paginas": Estaticas, "servicos": Servicos, "vagas": Vagas, "conteudos": Artigos, "institucional": Paginas}
