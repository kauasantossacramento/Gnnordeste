import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AcompanharForm, CandidaturaForm, MensagemForm, PropostaForm
from .models import (Artigo, Candidatura, Cliente, Configuracao, Depoimento, Etapa, Numero, Pagina,
                     Pergunta, Pilar, Proposta, Secao, Segmento, Servico, Vaga)

log = logging.getLogger(__name__)


def _avisar_equipe(assunto, corpo):
    destino = Configuracao.carregar().email_notificacoes
    if not destino:
        return
    try:
        send_mail(assunto, corpo, settings.DEFAULT_FROM_EMAIL, [destino])
    except Exception:  # e-mail nunca derruba o formulário
        log.exception("Falha ao enviar notificação por e-mail")


def _base():
    return {
        "servicos": Servico.objects.filter(ativo=True),
        "pilares": Pilar.objects.filter(ativo=True),
        "etapas": Etapa.objects.filter(ativo=True),
        "numeros": Numero.objects.filter(ativo=True),
        "segmentos": Segmento.objects.filter(ativo=True),
        "perguntas": Pergunta.objects.filter(ativo=True),
        "depoimentos": Depoimento.objects.filter(ativo=True),
        "clientes": Cliente.objects.filter(ativo=True),
    }


def home(request):
    ctx = _base()
    ctx.update({
        "vagas": Vaga.abertas().filter(destaque=True)[:4],
        "total_vagas": Vaga.abertas().count(),
        "artigos": Artigo.objects.filter(publicado=True)[:3],
    })
    return render(request, "core/home.html", ctx)


def sobre(request):
    return render(request, "core/sobre.html", _base())


def servicos(request):
    return render(request, "core/servicos.html", _base())


def servico(request, slug):
    s = get_object_or_404(Servico, slug=slug, ativo=True)
    return render(request, "core/servico.html", {
        "s": s, "outros": Servico.objects.filter(ativo=True).exclude(pk=s.pk),
        "vagas": Vaga.abertas().filter(area=s)[:3], "perguntas": Pergunta.objects.filter(ativo=True)[:5]})


def proposta(request):
    if request.method == "POST":
        form = PropostaForm(request.POST)
        if form.is_valid():
            p = form.save()
            _avisar_equipe(f"[Site] Nova proposta {p.protocolo} — {p.empresa}",
                           f"{p.nome} ({p.cargo}) <{p.email}> {p.telefone}\n"
                           f"{p.profissionais} profissionais · {p.cidade}/{p.uf}\n"
                           f"Serviços: {', '.join(s.titulo for s in p.servicos.all())}\n\n{p.mensagem}")
            request.session["proposta_ok"] = p.pk
            return redirect(reverse("core:proposta") + "?enviada=1")
        messages.error(request, "Faltam algumas informações. Confira os campos destacados.")
    else:
        qtd = request.GET.get("profissionais", "10")
        form = PropostaForm(initial={"servicos": request.GET.getlist("servico"),
                                     "profissionais": int(qtd) if qtd.isdigit() and 0 < int(qtd) <= 5000 else 10})
    enviada = None
    if request.GET.get("enviada"):
        enviada = Proposta.objects.filter(pk=request.session.pop("proposta_ok", None)).first()
    return render(request, "core/proposta.html", {
        "form": form, "enviada": enviada, "servicos": Servico.objects.filter(ativo=True),
        "selecionados": [str(x) for x in (form["servicos"].value() or [])],
        "etapas_sim": Secao.objects.filter(chave="proposta_etapas").first().lista
        if Secao.objects.filter(chave="proposta_etapas").exists() else [],
        "perguntas": Pergunta.objects.filter(ativo=True)[:4]})


def _candidatura(request, vaga=None):
    vagas = Vaga.abertas()
    if request.method == "POST":
        form = CandidaturaForm(request.POST, request.FILES, vagas=vagas)
        if form.is_valid():
            c = form.save(commit=False)
            c.vaga = c.vaga or vaga
            c.save()
            _avisar_equipe(f"[Site] Candidatura {c.protocolo}: {c.nome}",
                           f"{c.nome} <{c.email}> {c.telefone}\nVaga: {c.vaga or 'Banco de talentos'}")
            request.session["candidatura_ok"] = c.pk
            return redirect(request.path + "?enviada=1#candidatura"), None
        messages.error(request, "Não foi possível enviar. Confira os campos destacados.")
    else:
        form = CandidaturaForm(vagas=vagas, initial={"vaga": vaga.pk if vaga else None})
    return None, form


def _enviada(request):
    if request.GET.get("enviada"):
        return Candidatura.objects.filter(pk=request.session.pop("candidatura_ok", None)).first()
    return None


def carreiras(request):
    resp, form = _candidatura(request)
    if resp:
        return resp
    vagas = Vaga.abertas()
    return render(request, "core/carreiras.html", {
        "form": form, "vagas": vagas, "enviada": _enviada(request),
        "cidades": sorted({v.local for v in vagas}),
        "areas": sorted({v.area.titulo for v in vagas if v.area}),
        "pilares": Pilar.objects.filter(ativo=True)})


def vaga(request, slug):
    v = get_object_or_404(Vaga.objects.select_related("area"), slug=slug, ativo=True)
    resp, form = _candidatura(request, v)
    if resp:
        return resp
    return render(request, "core/vaga.html", {
        "v": v, "form": form, "enviada": _enviada(request), "outras": Vaga.abertas().exclude(pk=v.pk)[:3]})


def acompanhar(request):
    form, resultado = AcompanharForm(request.GET or None), None
    if request.GET and form.is_valid():
        resultado = (Candidatura.objects.select_related("vaga")
                     .filter(protocolo__iexact=form.cleaned_data["protocolo"].strip(),
                             email__iexact=form.cleaned_data["email"].strip()).first()) or "nao-encontrada"
    passos = []
    if isinstance(resultado, Candidatura):
        ordem = ["recebida", "triagem", "entrevista", "aprovada"]
        atual = ordem.index(resultado.status) if resultado.status in ordem else 1
        passos = [{"nome": n, "estado": "feito" if i < atual else ("atual" if i == atual else "")}
                  for i, n in enumerate(["Recebida", "Em triagem", "Entrevista", "Aprovada"])]
    return render(request, "core/acompanhar.html", {"form": form, "resultado": resultado, "passos": passos})


def conteudos(request):
    qs = Artigo.objects.filter(publicado=True)
    cat = request.GET.get("categoria", "")
    if cat:
        qs = qs.filter(categoria=cat)
    pagina = Paginator(qs, 9).get_page(request.GET.get("p"))
    return render(request, "core/conteudos.html", {"pagina": pagina, "categoria": cat,
                                                   "categorias": Artigo.CATEGORIAS})


def artigo(request, slug):
    a = get_object_or_404(Artigo, slug=slug, publicado=True)
    return render(request, "core/artigo.html", {
        "a": a, "outros": Artigo.objects.filter(publicado=True).exclude(pk=a.pk)[:3]})


def contato(request):
    if request.method == "POST":
        form = MensagemForm(request.POST)
        if form.is_valid():
            msg = form.save()
            _avisar_equipe(f"[Site] Contato: {msg.nome}", f"{msg.nome} <{msg.email}> {msg.telefone}\n\n{msg.mensagem}")
            messages.success(request, "Mensagem enviada! Retornaremos em breve.")
            return redirect("core:contato")
        messages.error(request, "Confira os campos destacados.")
    else:
        form = MensagemForm(initial={"assunto": request.GET.get("assunto", "duvida")})
    return render(request, "core/contato.html", {"form": form, "perguntas": Pergunta.objects.filter(ativo=True)})


def pagina(request, slug):
    return render(request, "core/pagina.html", {"pg": get_object_or_404(Pagina, slug=slug, publicado=True)})


def robots_txt(request):
    linhas = ["User-agent: *", "Disallow: /painel/", "Allow: /",
              f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml"]
    return HttpResponse("\n".join(linhas) + "\n", content_type="text/plain")


def erro_404(request, exception):
    return render(request, "404.html", status=404)
