from django.contrib import admin
from django.utils.html import format_html

from . import models


def miniatura(campo, tamanho=60):
    def _thumb(*args):  # usado como método do ModelAdmin: (self, obj)
        img = getattr(args[-1], campo)
        if img:
            return format_html(
                '<img src="{}" style="height:{}px;width:{}px;object-fit:cover;border-radius:8px">',
                img.url, tamanho, int(tamanho * 1.4))
        return "—"
    _thumb.short_description = "imagem"
    return _thumb


@admin.action(description="Ativar selecionados")
def ativar(modeladmin, request, queryset):
    queryset.update(ativo=True)


@admin.action(description="Desativar selecionados")
def desativar(modeladmin, request, queryset):
    queryset.update(ativo=False)


@admin.register(models.ConfiguracaoSite)
class ConfiguracaoSiteAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Empresa", {"fields": ("nome", "slogan", "meta_descricao")}),
        ("Logos", {"fields": ("logo", "logo_branca")}),
        ("Contato", {"fields": ("telefone", "whatsapp", "email", "email_recebimento",
                                "endereco", "horario", "mapa_embed")}),
        ("Redes sociais", {"fields": ("texto_redes", "instagram", "facebook", "linkedin", "youtube")}),
    )

    def has_add_permission(self, request):
        return not models.ConfiguracaoSite.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.Secao)
class SecaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "pagina", "titulo", "ativo", "thumb")
    list_filter = ("pagina", "ativo")
    list_editable = ("ativo",)
    search_fields = ("nome", "titulo", "texto")
    readonly_fields = ("chave",)
    thumb = miniatura("imagem", 40)
    fieldsets = (
        (None, {"fields": ("nome", "pagina", "chave", "ativo")}),
        ("Textos", {"fields": ("sobretitulo", "titulo", "destaque", "subtitulo", "texto", "itens")}),
        ("Imagem e botão", {"fields": ("imagem", "botao_texto", "botao_link")}),
    )

    def has_add_permission(self, request):
        # Seções são criadas pelo sistema (cada uma corresponde a um bloco do layout).
        return request.user.is_superuser

    def get_readonly_fields(self, request, obj=None):
        return () if obj is None else ("chave",)


@admin.register(models.Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "formato", "local", "inicio", "fim", "ativo", "ordem")
    list_filter = ("formato", "tipo", "local", "ativo")
    list_editable = ("ativo", "ordem")
    search_fields = ("titulo", "texto")
    autocomplete_fields = ("vaga",)
    actions = (ativar, desativar)
    fieldsets = (
        ("Conteúdo", {"fields": ("tipo", "titulo", "texto", "imagem")}),
        ("Onde e como aparece", {
            "fields": ("formato", "local", "frequencia", "ativo", "ordem"),
            "description": "Cartão em seção: aparece no local escolhido. Modal: abre uma janela ao "
                           "entrar na página. Faixa: barra fina no topo do site.",
        }),
        ("Botão / anexo", {"fields": ("vaga", "botao_texto", "botao_link", "anexo")}),
        ("Período", {"fields": ("inicio", "fim")}),
    )


class CandidaturaInline(admin.TabularInline):
    model = models.Candidatura
    extra = 0
    fields = ("nome", "telefone", "email", "status", "curriculo", "criado_em")
    readonly_fields = ("nome", "telefone", "email", "curriculo", "criado_em")
    show_change_link = True
    can_delete = False


@admin.register(models.Vaga)
class VagaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "local_exibicao", "regime", "quantidade", "prazo", "destaque",
                    "ativo", "total_candidaturas")
    list_filter = ("ativo", "regime", "unidade", "destaque")
    list_editable = ("ativo", "destaque")
    search_fields = ("titulo", "resumo", "descricao")
    prepopulated_fields = {"slug": ("titulo",)}
    autocomplete_fields = ("unidade",)
    actions = (ativar, desativar)
    inlines = (CandidaturaInline,)
    fieldsets = (
        ("Vaga", {"fields": ("titulo", "slug", "resumo", "regime", "quantidade", "salario")}),
        ("Local", {"fields": ("unidade", "local")}),
        ("Detalhes", {"fields": ("descricao", "requisitos", "edital", "link_externo")}),
        ("Publicação", {"fields": ("prazo", "destaque", "ativo", "ordem")}),
    )

    @admin.display(description="candidaturas")
    def total_candidaturas(self, obj):
        return obj.candidaturas.count()


@admin.register(models.Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = ("nome", "vaga", "telefone", "email", "cidade", "status", "criado_em", "cv")
    list_filter = ("status", "vaga", "criado_em")
    list_editable = ("status",)
    search_fields = ("nome", "email", "telefone", "cidade")
    readonly_fields = ("vaga", "nome", "email", "telefone", "cidade", "curriculo", "mensagem", "criado_em")
    fields = readonly_fields + ("status", "observacoes")
    date_hierarchy = "criado_em"

    @admin.display(description="currículo")
    def cv(self, obj):
        return format_html('<a href="{}" target="_blank">baixar</a>', obj.curriculo.url) if obj.curriculo else "—"


@admin.register(models.Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ("thumb", "nome", "uf", "status", "sede", "ativo", "ordem")
    list_display_links = ("thumb", "nome")
    list_filter = ("status", "uf", "ativo")
    list_editable = ("status", "ativo", "ordem")
    search_fields = ("nome", "resumo")
    prepopulated_fields = {"slug": ("nome", "uf")}
    thumb = miniatura("imagem")
    actions = (ativar, desativar)


@admin.register(models.Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "icone", "ativo", "ordem")
    list_editable = ("ativo", "ordem")


@admin.register(models.Numero)
class NumeroAdmin(admin.ModelAdmin):
    list_display = ("__str__", "ativo", "ordem")
    list_editable = ("ativo", "ordem")


@admin.register(models.SlideHero)
class SlideHeroAdmin(admin.ModelAdmin):
    list_display = ("thumb", "legenda", "ativo", "ordem")
    list_editable = ("ativo", "ordem")
    thumb = miniatura("imagem")


@admin.register(models.ImagemGaleria)
class ImagemGaleriaAdmin(admin.ModelAdmin):
    list_display = ("thumb", "titulo", "ativo", "ordem")
    list_editable = ("ativo", "ordem")
    thumb = miniatura("imagem")


@admin.register(models.Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ("thumb", "titulo", "data", "publicado")
    list_display_links = ("thumb", "titulo")
    list_filter = ("publicado",)
    list_editable = ("publicado",)
    search_fields = ("titulo", "resumo", "conteudo")
    prepopulated_fields = {"slug": ("titulo",)}
    date_hierarchy = "data"
    thumb = miniatura("capa")


@admin.register(models.Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "ativo", "ordem")
    list_filter = ("categoria",)
    list_editable = ("ativo", "ordem")


@admin.register(models.MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "telefone", "assunto", "criado_em", "lida")
    list_filter = ("lida", "criado_em")
    list_editable = ("lida",)
    search_fields = ("nome", "email", "mensagem")
    readonly_fields = ("nome", "email", "telefone", "assunto", "mensagem", "criado_em")
    date_hierarchy = "criado_em"

    def has_add_permission(self, request):
        return False


@admin.register(models.Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ("protocolo", "categoria", "anonima", "status", "criado_em")
    list_filter = ("status", "categoria", "anonima")
    list_editable = ("status",)
    search_fields = ("protocolo", "relato")
    readonly_fields = ("protocolo", "categoria", "relato", "anonima", "nome", "contato", "criado_em")
    fields = readonly_fields + ("status", "resposta")

    def has_add_permission(self, request):
        return False
