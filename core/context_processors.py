from django.urls import resolve, Resolver404

from .models import Aviso, ConfiguracaoSite, Documento, Secao

# Nome da rota → "local" usado nos avisos
PAGINA_POR_ROTA = {
    "home": "home",
    "quem_somos": "quem-somos",
    "unidades": "unidades",
    "unidade": "unidades",
    "trabalhe": "trabalhe-conosco",
    "vaga": "trabalhe-conosco",
    "contato": "contato",
    "noticias": "noticias",
    "noticia": "noticias",
    "denuncias": "denuncias",
}


class Secoes(dict):
    """Permite usar {{ S.chave.titulo }} sem quebrar se a seção não existir."""

    def __missing__(self, key):
        return Secao(chave=key, ativo=False)


def site(request):
    if request.path.startswith("/painel"):
        return {}
    try:
        nome_rota = resolve(request.path_info).url_name
    except Resolver404:
        nome_rota = ""
    pagina = PAGINA_POR_ROTA.get(nome_rota, "")

    avisos = list(Aviso.vigentes())
    globais = [a for a in avisos if a.local in ("todas", pagina)]
    return {
        "CFG": ConfiguracaoSite.carregar(),
        "S": Secoes({s.chave: s for s in Secao.objects.all()}),
        "PAGINA": pagina,
        "AVISOS": avisos,
        "AVISOS_MODAL": [a for a in globais if a.formato == "modal"],
        "AVISOS_FAIXA": [a for a in globais if a.formato == "faixa"],
        "DOCS_ETICA": Documento.objects.filter(ativo=True, categoria="etica"),
    }
