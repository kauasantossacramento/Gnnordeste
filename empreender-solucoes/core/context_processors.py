from django.templatetags.static import static
from django.urls import Resolver404, resolve

from .models import Aviso, Configuracao, Pagina, Secao, Servico

ROTA_PARA_LOCAL = {
    "home": "home", "sobre": "sobre", "servicos": "servicos", "servico": "servicos",
    "carreiras": "carreiras", "vaga": "carreiras", "acompanhar": "carreiras",
    "proposta": "proposta", "contato": "contato", "conteudos": "conteudos", "artigo": "conteudos",
}


class Secoes(dict):
    """{{ S.chave.titulo }} funciona mesmo se o bloco ainda não existir."""

    def __missing__(self, key):
        return Secao(chave=key, ativo=False)


def site(request):
    if request.path.startswith("/painel"):
        return {}
    try:
        rota = resolve(request.path_info).url_name
    except Resolver404:
        rota = ""
    local = ROTA_PARA_LOCAL.get(rota, "")
    avisos = list(Aviso.vigentes())
    da_pagina = [a for a in avisos if a.local in ("todas", local)]
    cfg = Configuracao.carregar()

    def img(campo, padrao):
        f = getattr(cfg, campo)
        return f.url if f else static(padrao)

    marca = {
        "logo": img("logo", "img/logo.png"), "logo_negativa": img("logo_negativa", "img/logo-negativa.png"),
        "simbolo": img("simbolo", "img/simbolo.png"), "simbolo_negativo": img("simbolo_negativo", "img/simbolo-negativo.png"),
        "favicon": img("favicon", "img/favicon-32.png"), "og": img("imagem_compartilhamento", "img/og.jpg"),
    }
    return {
        "CFG": cfg,
        "MARCA": marca,
        "S": Secoes({s.chave: s for s in Secao.objects.all()}),
        "ROTA": rota,
        "LOCAL": local,
        "AVISOS": avisos,
        "AVISOS_MODAL": [a for a in da_pagina if a.formato == "modal"],
        "AVISOS_FAIXA": [a for a in da_pagina if a.formato == "faixa"],
        "AVISOS_FLUTUANTE": [a for a in da_pagina if a.formato == "flutuante"][:1],
        "MENU_SERVICOS": Servico.objects.filter(ativo=True),
        "PAGINAS_RODAPE": Pagina.objects.filter(publicado=True, no_rodape=True),
    }
