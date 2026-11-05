import re

from django import template
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag("partials/avisos_secao.html", takes_context=True)
def avisos(context, local):
    """Renderiza os avisos em formato 'cartão' de um local: {% avisos "home-servicos" %}"""
    return {"avisos": [a for a in context.get("AVISOS", []) if a.formato == "secao" and a.local == local]}


@register.filter
def destacar(titulo, trecho):
    """Envolve o trecho do título em <em> para receber a cor de destaque."""
    titulo = conditional_escape(titulo or "")
    if trecho:
        t = conditional_escape(trecho)
        titulo = titulo.replace(t, f"<em>{t}</em>", 1)
    return mark_safe(titulo)


@register.filter
def paragrafos(texto):
    partes = [p.strip() for p in re.split(r"\n\s*\n", texto or "") if p.strip()]
    return mark_safe("".join(
        format_html("<p>{}</p>", mark_safe(conditional_escape(p).replace("\n", "<br>"))) for p in partes))


@register.simple_tag
def icone(nome, classe="ico"):
    return mark_safe(f'<svg class="{classe}" aria-hidden="true"><use href="#i-{nome}"></use></svg>')
