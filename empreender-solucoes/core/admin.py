from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateFilter, RelatedDropdownFilter
from unfold.decorators import action, display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from . import models as m

# ------------------------------------------------------------------ usuários com o visual do painel
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


# ------------------------------------------------------------------ utilidades
def thumb(campo, rotulo="imagem"):
    @display(description=rotulo)
    def _f(self, obj):
        img = getattr(obj, campo)
        if not img:
            return "—"
        return format_html('<img src="{}" style="height:44px;width:64px;object-fit:cover;border-radius:8px">', img.url)
    return _f


class Base(ModelAdmin):
    list_filter_submit = True
    warn_unsaved_form = True
    compressed_fields = True


class OrdenavelAdmin(Base):
    list_editable = ("ordem", "ativo")
    actions = ("ativar", "desativar")

    @action(description="Mostrar no site")
    def ativar(self, request, qs):
        qs.update(ativo=True)

    @action(description="Ocultar do site")
    def desativar(self, request, qs):
        qs.update(ativo=False)


# ------------------------------------------------------------------ empresa e textos
@admin.register(m.Configuracao)
class ConfiguracaoAdmin(Base):
    fieldsets = (
        ("Empresa", {"fields": ("nome", "slogan", "descricao_curta", "cnpj")}),
        ("Logos e imagens da marca", {"fields": (("logo", "logo_negativa"), ("simbolo", "simbolo_negativo"),
                                                 ("favicon", "imagem_compartilhamento"))}),
        ("Contato", {"fields": ("telefone", "whatsapp", "email", "email_notificacoes", "horario")}),
        ("Endereço", {"fields": ("endereco", ("cidade", "uf"), "mapa_embed")}),
        ("Redes sociais", {"fields": ("instagram", "linkedin", "facebook", "youtube")}),
        ("Google e privacidade", {"fields": ("meta_descricao", "google_analytics", "texto_cookies")}),
    )

    def has_add_permission(self, request):
        return not m.Configuracao.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(m.Secao)
class SecaoAdmin(Base):
    list_display = ("nome", "pagina", "titulo", "ativo")
    list_filter = (("pagina", ChoicesDropdownFilter), "ativo")
    list_editable = ("ativo",)
    search_fields = ("nome", "titulo", "texto")
    fieldsets = (
        (None, {"fields": ("nome", "pagina", "chave", "ativo")}),
        ("Textos", {"fields": ("sobretitulo", "titulo", "destaque", "subtitulo", "texto", "itens")}),
        ("Imagem e botões", {"fields": ("imagem", ("botao_texto", "botao_link"), ("botao2_texto", "botao2_link"))}),
    )

    def get_readonly_fields(self, request, obj=None):
        return ("chave",) if obj else ()

    def has_add_permission(self, request):
        return request.user.is_superuser


@admin.register(m.Servico)
class ServicoAdmin(OrdenavelAdmin):
    list_display = ("titulo", "icone", "resumo", "ordem", "ativo")
    prepopulated_fields = {"slug": ("titulo",)}
    search_fields = ("titulo", "resumo")


@admin.register(m.Segmento)
class SegmentoAdmin(OrdenavelAdmin):
    list_display = ("titulo", "icone", "texto", "ordem", "ativo")


@admin.register(m.Pilar)
class PilarAdmin(OrdenavelAdmin):
    list_display = ("titulo", "texto", "ordem", "ativo")


@admin.register(m.Etapa)
class EtapaAdmin(OrdenavelAdmin):
    list_display = ("titulo", "texto", "ordem", "ativo")


@admin.register(m.Numero)
class NumeroAdmin(OrdenavelAdmin):
    list_display = ("__str__", "ordem", "ativo")


@admin.register(m.Pergunta)
class PerguntaAdmin(OrdenavelAdmin):
    list_display = ("pergunta", "ordem", "ativo")
    search_fields = ("pergunta", "resposta")


@admin.register(m.Depoimento)
class DepoimentoAdmin(OrdenavelAdmin):
    list_display = ("foto_", "nome", "empresa", "ordem", "ativo")
    foto_ = thumb("foto", "foto")


@admin.register(m.Cliente)
class ClienteAdmin(OrdenavelAdmin):
    list_display = ("logo_", "nome", "ordem", "ativo")
    logo_ = thumb("logo", "logo")


@admin.register(m.Pagina)
class PaginaAdmin(Base):
    list_display = ("titulo", "slug", "no_rodape", "publicado", "atualizado_em")
    list_editable = ("no_rodape", "publicado")
    prepopulated_fields = {"slug": ("titulo",)}


@admin.register(m.Artigo)
class ArtigoAdmin(Base):
    list_display = ("capa_", "titulo", "categoria", "data", "publicado")
    list_display_links = ("capa_", "titulo")
    list_filter = (("categoria", ChoicesDropdownFilter), "publicado")
    list_editable = ("publicado",)
    search_fields = ("titulo", "resumo", "conteudo")
    prepopulated_fields = {"slug": ("titulo",)}
    date_hierarchy = "data"
    capa_ = thumb("capa", "capa")


# ------------------------------------------------------------------ recrutamento
class CandidaturaInline(TabularInline):
    model = m.Candidatura
    extra = 0
    fields = ("protocolo", "nome", "telefone", "status", "criado_em")
    readonly_fields = ("protocolo", "nome", "telefone", "criado_em")
    show_change_link = True
    can_delete = False
    tab = True


@admin.register(m.Vaga)
class VagaAdmin(OrdenavelAdmin):
    list_display = ("titulo", "local", "regime", "quantidade", "prazo", "situacao", "total", "destaque", "ativo")
    list_editable = ("destaque", "ativo")
    list_filter = (("regime", ChoicesDropdownFilter), ("uf", ChoicesDropdownFilter),
                   ("area", RelatedDropdownFilter), "ativo")
    search_fields = ("titulo", "cidade", "resumo")
    prepopulated_fields = {"slug": ("titulo", "cidade")}
    inlines = (CandidaturaInline,)
    fieldsets = (
        ("Vaga", {"fields": ("titulo", "slug", "area", "resumo", ("regime", "modalidade"), "quantidade")}),
        ("Local", {"fields": (("cidade", "uf"),)}),
        ("Detalhes", {"fields": ("descricao", "requisitos", "beneficios", "salario", "edital")}),
        ("Publicação", {"fields": ("prazo", "destaque", "ativo", "ordem")}),
    )

    @display(description="situação", label={"Aberta": "success", "Encerrada": "danger", "Oculta": "info"})
    def situacao(self, obj):
        return "Oculta" if not obj.ativo else ("Aberta" if obj.aberta else "Encerrada")

    @display(description="candidaturas")
    def total(self, obj):
        return obj.candidaturas.count()


@admin.register(m.Candidatura)
class CandidaturaAdmin(Base):
    list_display = ("protocolo", "nome", "vaga", "telefone", "cidade", "status_", "criado_em", "cv")
    list_filter = (("status", ChoicesDropdownFilter), ("vaga", RelatedDropdownFilter), ("criado_em", RangeDateFilter))
    search_fields = ("protocolo", "nome", "email", "telefone", "cidade")
    readonly_fields = ("protocolo", "vaga", "nome", "email", "telefone", "cidade", "linkedin", "curriculo",
                       "mensagem", "criado_em")
    fieldsets = (
        ("Candidato", {"fields": readonly_fields}),
        ("Andamento", {"fields": ("status", "retorno", "observacoes")}),
    )
    actions = ("marcar_triagem", "marcar_entrevista", "marcar_banco")
    date_hierarchy = "criado_em"

    @display(description="status", ordering="status", label={
        "Recebida": "info", "Em triagem": "warning", "Entrevista agendada": "warning",
        "Aprovada": "success", "Banco de talentos": "info", "Processo encerrado": "danger"})
    def status_(self, obj):
        return obj.get_status_display()

    @display(description="currículo")
    def cv(self, obj):
        return format_html('<a href="{}" target="_blank">baixar</a>', obj.curriculo.url) if obj.curriculo else "—"

    def _status(self, request, qs, valor):
        n = qs.update(status=valor)
        messages.success(request, f"{n} candidatura(s) atualizada(s).")

    @action(description="Mover para triagem")
    def marcar_triagem(self, request, qs):
        self._status(request, qs, "triagem")

    @action(description="Marcar entrevista agendada")
    def marcar_entrevista(self, request, qs):
        self._status(request, qs, "entrevista")

    @action(description="Mover para banco de talentos")
    def marcar_banco(self, request, qs):
        self._status(request, qs, "banco")

    def has_add_permission(self, request):
        return False


# ------------------------------------------------------------------ comercial
@admin.register(m.Proposta)
class PropostaAdmin(Base):
    list_display = ("protocolo", "empresa", "nome", "profissionais", "local", "setor", "status_", "criado_em")
    list_filter = (("status", ChoicesDropdownFilter), ("setor", ChoicesDropdownFilter),
                   ("uf", ChoicesDropdownFilter), ("criado_em", RangeDateFilter))
    search_fields = ("protocolo", "empresa", "nome", "email", "cidade")
    readonly_fields = ("protocolo", "lista_servicos", "perfis", "profissionais", "contrato", "inicio", "setor",
                       "cidade", "uf", "empresa", "nome", "cargo", "email", "telefone", "mensagem", "criado_em")
    fieldsets = (
        ("Pedido", {"fields": ("protocolo", "lista_servicos", "perfis", "profissionais", "contrato", "inicio",
                               "setor", ("cidade", "uf"), "mensagem")}),
        ("Contato", {"fields": ("empresa", "nome", "cargo", "email", "telefone", "criado_em")}),
        ("Andamento comercial", {"fields": ("status", "observacoes")}),
    )
    date_hierarchy = "criado_em"

    @display(description="serviços")
    def lista_servicos(self, obj):
        return ", ".join(s.titulo for s in obj.servicos.all()) or "—"

    @display(description="local")
    def local(self, obj):
        return f"{obj.cidade}/{obj.uf}"

    @display(description="status", ordering="status", label={
        "Nova": "danger", "Em contato": "warning", "Proposta enviada": "info",
        "Contrato fechado": "success", "Não avançou": "info"})
    def status_(self, obj):
        return obj.get_status_display()

    def has_add_permission(self, request):
        return False


@admin.register(m.Mensagem)
class MensagemAdmin(Base):
    list_display = ("nome", "email", "assunto", "criado_em", "lida")
    list_filter = (("assunto", ChoicesDropdownFilter), "lida")
    list_editable = ("lida",)
    search_fields = ("nome", "email", "mensagem")
    readonly_fields = ("nome", "email", "telefone", "assunto", "mensagem", "criado_em")

    def has_add_permission(self, request):
        return False


@admin.register(m.Aviso)
class AvisoAdmin(OrdenavelAdmin):
    list_display = ("titulo", "tipo", "formato", "local", "no_ar_", "inicio", "fim", "ordem", "ativo")
    list_filter = (("formato", ChoicesDropdownFilter), ("tipo", ChoicesDropdownFilter),
                   ("local", ChoicesDropdownFilter), "ativo")
    search_fields = ("titulo", "texto")
    autocomplete_fields = ("vaga",)
    fieldsets = (
        ("Conteúdo", {"fields": ("tipo", "titulo", "texto", "imagem")}),
        ("Onde e como aparece", {
            "fields": ("formato", "local", "frequencia", ("ativo", "ordem")),
            "description": "Seção: cartão dentro da página. Modal: janela ao abrir. Faixa: barra no topo. "
                           "Flutuante: cartão discreto no canto inferior.",
        }),
        ("Botão e anexo", {"fields": ("vaga", ("botao_texto", "botao_link"), "anexo")}),
        ("Período", {"fields": (("inicio", "fim"),)}),
    )

    @display(description="no ar?", label={"No ar": "success", "Fora do ar": "danger"})
    def no_ar_(self, obj):
        return "No ar" if obj.no_ar else "Fora do ar"
