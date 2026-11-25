"""Dados do painel inicial (/painel/)."""
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from .models import Aviso, Candidatura, Mensagem, Proposta, Vaga


def dashboard_callback(request, context):
    hoje = timezone.now()
    ultimos = hoje - timedelta(days=30)
    dias = [(hoje - timedelta(days=i)).date() for i in range(13, -1, -1)]
    prop = Proposta.objects.filter(criado_em__date__gte=dias[0]).values_list("criado_em", flat=True)
    cand = Candidatura.objects.filter(criado_em__date__gte=dias[0]).values_list("criado_em", flat=True)
    serie = []
    for d in dias:
        p = sum(1 for x in prop if timezone.localtime(x).date() == d)
        c = sum(1 for x in cand if timezone.localtime(x).date() == d)
        serie.append({"dia": d.strftime("%d/%m"), "p": p, "c": c})
    maximo = max([1] + [max(s["p"], s["c"]) for s in serie])
    for s in serie:
        s["hp"], s["hc"] = round(s["p"] / maximo * 100), round(s["c"] / maximo * 100)

    funil = dict(Proposta.objects.values_list("status").annotate(n=Count("id")))
    context.update({
        "kpis": [
            {"rotulo": "Propostas novas", "valor": funil.get("nova", 0), "icone": "request_quote",
             "link": "/painel/core/proposta/?status__exact=nova", "dica": "aguardando primeiro contato"},
            {"rotulo": "Candidaturas (30 dias)", "valor": Candidatura.objects.filter(criado_em__gte=ultimos).count(),
             "icone": "badge", "link": "/painel/core/candidatura/", "dica": "currículos recebidos"},
            {"rotulo": "Vagas abertas", "valor": Vaga.abertas().count(), "icone": "work",
             "link": "/painel/core/vaga/", "dica": "publicadas no site"},
            {"rotulo": "Avisos no ar", "valor": Aviso.vigentes().count(), "icone": "campaign",
             "link": "/painel/core/aviso/", "dica": "modal, faixa, seção ou flutuante"},
        ],
        "serie": serie,
        "funil": [(rot, funil.get(k, 0)) for k, rot in Proposta.STATUS],
        "propostas": Proposta.objects.prefetch_related("servicos")[:6],
        "candidaturas": Candidatura.objects.select_related("vaga")[:6],
        "nao_lidas": Mensagem.objects.filter(lida=False).count(),
    })
    return context
