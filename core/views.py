import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CandidaturaForm, ContatoForm, DenunciaForm, ProtocoloForm
from .models import (ConfiguracaoSite, Denuncia, Documento, ImagemGaleria, Noticia, Numero,
                     Servico, SlideHero, Unidade, Vaga)

log = logging.getLogger(__name__)


def _notificar(assunto, corpo):
    destino = ConfiguracaoSite.carregar().email_recebimento
    if not destino:
        return
    try:
        send_mail(assunto, corpo, settings.DEFAULT_FROM_EMAIL, [destino], fail_silently=False)
    except Exception:  # o envio de e-mail nunca deve derrubar o formulário
        log.exception("Falha ao enviar e-mail de notificação")


def _contato_post(request, redirect_to):
    form = ContatoForm(request.POST)
    if form.is_valid():
        msg = form.save()
        _notificar(f"[Site] Contato de {msg.nome}",
                   f"{msg.nome} <{msg.email}> {msg.telefone}\n\n{msg.assunto}\n\n{msg.mensagem}")
        messages.success(request, "Mensagem enviada! Nossa equipe responderá em breve.")
        return redirect(redirect_to), form
    messages.error(request, "Confira os campos destacados e tente novamente.")
    return None, form


def home(request):
    form = ContatoForm()
    if request.method == "POST":
        resp, form = _contato_post(request, reverse("core:home") + "#contato")
        if resp:
            return resp
    return render(request, "core/home.html", {
        "slides": SlideHero.objects.filter(ativo=True),
        "servicos": Servico.objects.filter(ativo=True),
        "numeros": Numero.objects.filter(ativo=True),
        "unidades": Unidade.objects.filter(ativo=True),
        "vagas": Vaga.abertas().filter(destaque=True)[:3],
        "galeria": ImagemGaleria.objects.filter(ativo=True)[:6],
        "noticias": Noticia.objects.filter(publicado=True)[:3],
        "editais": Documento.objects.filter(ativo=True, categoria="edital"),
        "form": form,
    })


def quem_somos(request):
    return render(request, "core/quem_somos.html", {
        "numeros": Numero.objects.filter(ativo=True),
        "servicos": Servico.objects.filter(ativo=True),
        "galeria": ImagemGaleria.objects.filter(ativo=True),
    })


def unidades(request):
    todas = Unidade.objects.filter(ativo=True)
    return render(request, "core/unidades.html", {
        "ativas": [u for u in todas if u.status == "ativa"],
        "implantacao": [u for u in todas if u.status == "implantacao"],
        "estados": sorted({u.uf for u in todas}),
    })


def unidade(request, slug):
    u = get_object_or_404(Unidade, slug=slug, ativo=True)
    return render(request, "core/unidade.html", {
        "u": u,
        "vagas": Vaga.abertas().filter(unidade=u),
        "outras": Unidade.objects.filter(ativo=True).exclude(pk=u.pk)[:4],
    })


def _candidatura(request, vaga=None):
    vagas = Vaga.abertas()
    if request.method == "POST":
        form = CandidaturaForm(request.POST, request.FILES, vagas=vagas)
        if form.is_valid():
            c = form.save(commit=False)
            if vaga and not c.vaga:
                c.vaga = vaga
            c.save()
            _notificar(f"[Site] Nova candidatura: {c.nome}",
                       f"{c.nome} <{c.email}> {c.telefone}\nVaga: {c.vaga or 'Banco de talentos'}\n\n{c.mensagem}")
            messages.success(request, "Candidatura enviada com sucesso! Boa sorte 🍀")
            return redirect(request.path + "#candidatura"), form
        messages.error(request, "Não foi possível enviar. Confira os campos destacados.")
    else:
        form = CandidaturaForm(vagas=vagas, initial={"vaga": vaga.pk if vaga else None})
    return None, form


def trabalhe(request):
    resp, form = _candidatura(request)
    if resp:
        return resp
    vagas = Vaga.abertas()
    return render(request, "core/trabalhe.html", {
        "vagas": vagas,
        "unidades_com_vagas": sorted({v.local_exibicao for v in vagas}),
        "editais": Documento.objects.filter(ativo=True, categoria="edital"),
        "form": form,
    })


def vaga(request, slug):
    v = get_object_or_404(Vaga.objects.select_related("unidade"), slug=slug, ativo=True)
    resp, form = _candidatura(request, v)
    if resp:
        return resp
    return render(request, "core/vaga.html", {"v": v, "form": form,
                                              "outras": Vaga.abertas().exclude(pk=v.pk)[:3]})


def noticias(request):
    pagina = Paginator(Noticia.objects.filter(publicado=True), 9).get_page(request.GET.get("p"))
    return render(request, "core/noticias.html", {"pagina": pagina})


def noticia(request, slug):
    n = get_object_or_404(Noticia, slug=slug, publicado=True)
    return render(request, "core/noticia.html", {
        "n": n, "outras": Noticia.objects.filter(publicado=True).exclude(pk=n.pk)[:3]})


def contato(request):
    form = ContatoForm()
    if request.method == "POST":
        resp, form = _contato_post(request, reverse("core:contato"))
        if resp:
            return resp
    return render(request, "core/contato.html", {"form": form})


def denuncias(request):
    form, consulta, resultado = DenunciaForm(), ProtocoloForm(), None
    if request.method == "POST" and "relato" in request.POST:
        form = DenunciaForm(request.POST)
        if form.is_valid():
            d = form.save()
            _notificar("[Site] Nova denúncia recebida", f"Protocolo {d.protocolo} — {d.get_categoria_display()}")
            request.session["protocolo"] = d.protocolo
            return redirect(reverse("core:denuncias") + "?enviada=1")
        messages.error(request, "Descreva o ocorrido para enviar a denúncia.")
    elif request.GET.get("protocolo"):
        consulta = ProtocoloForm(request.GET)
        if consulta.is_valid():
            resultado = Denuncia.objects.filter(
                protocolo__iexact=consulta.cleaned_data["protocolo"].strip()).first() or "nao-encontrado"
    protocolo = request.session.pop("protocolo", None) if request.GET.get("enviada") else None
    return render(request, "core/denuncias.html", {
        "form": form, "consulta": consulta, "resultado": resultado, "protocolo": protocolo})


def erro_404(request, exception):
    return render(request, "404.html", status=404)
