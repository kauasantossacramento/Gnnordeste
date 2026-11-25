import json
import re

from django import template
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def destacar(titulo, trecho):
    """Envolve o trecho do título em <em> (dourado/itálico)."""
    titulo = conditional_escape(titulo or "")
    if trecho:
        t = conditional_escape(trecho)
        titulo = titulo.replace(t, f"<em>{t}</em>", 1)
    return mark_safe(titulo)


@register.filter
def paragrafos(texto):
    """Linha em branco = novo parágrafo; '## ' no início = subtítulo."""
    html = []
    for bloco in re.split(r"\n\s*\n", texto or ""):
        bloco = bloco.strip()
        if not bloco:
            continue
        if bloco.startswith("## "):
            html.append(format_html("<h2>{}</h2>", bloco[3:].strip()))
        else:
            html.append(format_html("<p>{}</p>", mark_safe(conditional_escape(bloco).replace("\n", "<br>"))))
    return mark_safe("".join(html))


@register.simple_tag
def icone(nome, classe="i"):
    return format_html('<svg class="{}" aria-hidden="true"><use href="#i-{}"></use></svg>', classe, nome)


@register.inclusion_tag("partials/avisos_secao.html", takes_context=True)
def avisos(context, local):
    """{% avisos "home-servicos" %} → cartões de aviso daquele local."""
    return {"avisos": [a for a in context.get("AVISOS", []) if a.formato == "secao" and a.local == local]}


@register.filter
def jsonld(dados):
    """Serializa dados estruturados (schema.org) com segurança dentro de <script>."""
    texto = json.dumps(dados, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e")
    return mark_safe(f'<script type="application/ld+json">{texto}</script>')


@register.simple_tag(takes_context=True)
def url_absoluta(context, caminho=""):
    from django.conf import settings
    req = context.get("request")
    base = settings.SITE_URL or (f"{req.scheme}://{req.get_host()}" if req else "")
    return base + caminho


@register.simple_tag(takes_context=True)
def org_jsonld(context):
    """Organization (schema.org) para o Google entender quem é a empresa."""
    from django.templatetags.static import static
    cfg = context.get("CFG")
    if not cfg:
        return ""
    base = url_absoluta(context)
    dados = {
        "@context": "https://schema.org", "@type": "Organization", "name": cfg.nome, "url": base + "/",
        "logo": base + static("img/logo.png"), "description": cfg.meta_descricao,
        "sameAs": [u for _, u in cfg.redes],
    }
    if cfg.telefone or cfg.email:
        dados["contactPoint"] = {"@type": "ContactPoint", "contactType": "customer service",
                                 "telephone": cfg.telefone or None, "email": cfg.email or None,
                                 "areaServed": "BR", "availableLanguage": "Portuguese"}
    if cfg.cidade:
        dados["address"] = {"@type": "PostalAddress", "streetAddress": cfg.endereco, "addressLocality": cfg.cidade,
                            "addressRegion": cfg.uf, "addressCountry": "BR"}
    return jsonld(dados)


@register.simple_tag(takes_context=True)
def vaga_jsonld(context, v):
    """JobPosting: faz a vaga aparecer no Google Vagas."""
    cfg = context.get("CFG")
    base = url_absoluta(context)
    dados = {
        "@context": "https://schema.org", "@type": "JobPosting", "title": v.titulo,
        "description": "<p>" + "</p><p>".join([v.resumo] + [x for x in v.descricao.split("\n") if x.strip()]) + "</p>",
        "datePosted": v.criado_em.date().isoformat(),
        "employmentType": v.GOOGLE_REGIME.get(v.regime, "OTHER"),
        "hiringOrganization": {"@type": "Organization", "name": cfg.nome, "sameAs": base + "/"},
        "jobLocation": {"@type": "Place", "address": {"@type": "PostalAddress", "addressLocality": v.cidade,
                                                      "addressRegion": v.uf, "addressCountry": "BR"}},
        "totalJobOpenings": v.quantidade, "directApply": True, "url": base + v.get_absolute_url(),
    }
    if v.prazo:
        dados["validThrough"] = v.prazo.isoformat() + "T23:59:59-03:00"
    if v.modalidade == "remoto":
        dados["jobLocationType"] = "TELECOMMUTE"
    return jsonld(dados)


@register.simple_tag
def faq_jsonld(perguntas):
    perguntas = list(perguntas)
    if not perguntas:
        return ""
    return jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": p.pergunta, "acceptedAnswer": {"@type": "Answer", "text": p.resposta}}
        for p in perguntas]})


@register.filter
def partes(texto, sep="|"):
    """'Título | texto' → ['Título', 'texto']"""
    p = [x.strip() for x in (texto or "").split(sep, 1)]
    return p + [""] * (2 - len(p))


@register.filter
def troca(texto, valor):
    """Substitui {nome} / {servico} no texto editável pelo valor da página."""
    return (texto or "").replace("{servico}", str(valor).lower()).replace("{nome}", str(valor))
