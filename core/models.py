"""Modelos de conteúdo do site do Grupo Nordeste.

Tudo que aparece no site pode ser editado pelo painel (/painel/):
textos das seções, imagens, unidades, vagas, avisos (em seção, faixa ou modal),
notícias e documentos. Formulários enviados pelo site também ficam salvos aqui.
"""
import secrets

from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

DOC_VALIDATOR = FileExtensionValidator(["pdf", "doc", "docx", "odt", "jpg", "jpeg", "png"])


class Ordenavel(models.Model):
    ordem = models.PositiveIntegerField("ordem", default=0, help_text="Menor aparece primeiro.")
    ativo = models.BooleanField("ativo/visível", default=True)

    class Meta:
        abstract = True
        ordering = ["ordem", "id"]


# --------------------------------------------------------------------------- Configuração
class ConfiguracaoSite(models.Model):
    """Registro único com dados gerais da empresa."""

    nome = models.CharField("nome da empresa", max_length=120, default="Grupo Nordeste")
    slogan = models.CharField(
        "slogan", max_length=200, default="Excelência em Terceirização de Serviços em todo o Brasil"
    )
    logo = models.ImageField("logo (fundo claro)", upload_to="site/", blank=True,
                             help_text="Deixe vazio para usar a logo padrão.")
    logo_branca = models.ImageField("logo (fundo escuro)", upload_to="site/", blank=True)
    telefone = models.CharField("telefone", max_length=40, default="(71) 2132-7708")
    whatsapp = models.CharField("WhatsApp (só números, com DDI)", max_length=20, blank=True,
                                help_text="Ex.: 557121327708. Exibe o botão flutuante do WhatsApp.")
    email = models.EmailField("e-mail", default="gruponordesteservicos@gmail.com")
    email_recebimento = models.EmailField(
        "e-mail que recebe formulários", blank=True,
        help_text="Opcional. Exige SMTP configurado no servidor.")
    endereco = models.TextField(
        "endereço",
        default="Av. Tancredo Neves nº 1632, SL 312 e 313, Torre Norte. Ed. Salvador Trade Center, "
                "Caminho das Árvores, Salvador/BA.",
    )
    mapa_embed = models.URLField("link de incorporação do Google Maps", blank=True, max_length=800,
                                 help_text="Google Maps → Compartilhar → Incorporar mapa → copie só o link do src.")
    horario = models.CharField("horário de atendimento", max_length=120,
                               default="Segunda a sexta, 8h às 18h")
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    texto_redes = models.CharField("texto sobre redes sociais", max_length=120,
                                   default="Em breve estaremos em todos os canais!")
    meta_descricao = models.CharField(
        "descrição para o Google", max_length=300,
        default="Grupo Nordeste: administração, gerenciamento de serviços e terceirização de mão de obra "
                "para o setor público e privado em todo o Brasil.",
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "configuração do site"
        verbose_name_plural = "⚙️ Configurações do site"

    def __str__(self):
        return "Configurações gerais"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def carregar(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def telefone_link(self):
        return "".join(c for c in self.telefone if c.isdigit() or c == "+")


# --------------------------------------------------------------------------- Seções de texto
class Secao(models.Model):
    """Bloco de texto editável. Cada seção do site tem uma chave fixa."""

    PAGINAS = [
        ("home", "Página inicial"),
        ("quem-somos", "Quem somos"),
        ("unidades", "Unidades"),
        ("trabalhe-conosco", "Trabalhe conosco"),
        ("contato", "Contato"),
        ("noticias", "Notícias"),
        ("denuncias", "Canal de denúncias"),
    ]
    chave = models.SlugField("identificador", max_length=60, unique=True,
                             help_text="Usado pelo site para localizar o bloco. Não altere.")
    pagina = models.CharField("página", max_length=30, choices=PAGINAS, default="home")
    nome = models.CharField("nome interno", max_length=120)
    sobretitulo = models.CharField("sobretítulo (texto pequeno)", max_length=120, blank=True)
    titulo = models.CharField("título", max_length=200, blank=True)
    destaque = models.CharField("palavra em destaque no título", max_length=80, blank=True,
                                help_text="Trecho do título que aparece colorido.")
    subtitulo = models.CharField("subtítulo", max_length=300, blank=True)
    texto = models.TextField("texto", blank=True,
                             help_text="Deixe uma linha em branco para separar parágrafos.")
    itens = models.TextField("lista de itens", blank=True, help_text="Um item por linha.")
    imagem = models.ImageField("imagem", upload_to="secoes/", blank=True)
    botao_texto = models.CharField("texto do botão", max_length=60, blank=True)
    botao_link = models.CharField("link do botão", max_length=300, blank=True)
    ativo = models.BooleanField("exibir seção", default=True)

    class Meta:
        verbose_name = "seção de texto"
        verbose_name_plural = "📝 Textos das seções"
        ordering = ["pagina", "id"]

    def __str__(self):
        return f"{self.get_pagina_display()} › {self.nome}"

    @property
    def lista(self):
        return [i.strip(" -•;") for i in self.itens.splitlines() if i.strip()]


# --------------------------------------------------------------------------- Avisos
class Aviso(Ordenavel):
    """Aviso que pode aparecer dentro de uma seção, numa faixa no topo ou em uma janela (modal)."""

    TIPOS = [
        ("contratacao", "📢 Contratação / Vagas"),
        ("edital", "📄 Edital / Processo seletivo"),
        ("informativo", "ℹ️ Informativo"),
        ("urgente", "⚠️ Urgente"),
        ("evento", "🎉 Evento / Novidade"),
    ]
    FORMATOS = [
        ("secao", "Cartão dentro da seção escolhida"),
        ("modal", "Janela (modal) ao abrir a página"),
        ("faixa", "Faixa fina no topo do site"),
    ]
    LOCAIS = [
        ("todas", "Todas as páginas"),
        ("home", "Início — topo (abaixo do banner)"),
        ("home-servicos", "Início — seção Serviços"),
        ("home-trabalhe", "Início — seção Trabalhe Conosco"),
        ("quem-somos", "Quem somos"),
        ("unidades", "Unidades"),
        ("trabalhe-conosco", "Trabalhe conosco"),
        ("contato", "Contato"),
        ("noticias", "Notícias"),
    ]
    FREQUENCIAS = [
        ("sessao", "Uma vez por visita"),
        ("sempre", "Sempre que abrir a página"),
        ("uma-vez", "Só uma vez por visitante"),
    ]

    tipo = models.CharField("tipo", max_length=20, choices=TIPOS, default="contratacao")
    formato = models.CharField("como exibir", max_length=10, choices=FORMATOS, default="secao")
    local = models.CharField("onde exibir", max_length=20, choices=LOCAIS, default="home")
    titulo = models.CharField("título", max_length=160)
    texto = models.TextField("texto", blank=True)
    imagem = models.ImageField("imagem", upload_to="avisos/", blank=True)
    botao_texto = models.CharField("texto do botão", max_length=60, blank=True)
    botao_link = models.CharField("link do botão", max_length=300, blank=True)
    vaga = models.ForeignKey("Vaga", verbose_name="vaga relacionada", null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="avisos",
                             help_text="Se escolher uma vaga, o botão leva para ela.")
    anexo = models.FileField("anexo (PDF/edital)", upload_to="avisos/", blank=True,
                             validators=[DOC_VALIDATOR])
    inicio = models.DateTimeField("mostrar a partir de", default=timezone.now)
    fim = models.DateTimeField("mostrar até", null=True, blank=True,
                               help_text="Vazio = sem data para sair do ar.")
    frequencia = models.CharField("frequência do modal", max_length=10, choices=FREQUENCIAS,
                                  default="sessao")
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "aviso"
        verbose_name_plural = "📢 Avisos (seção, faixa e modal)"

    def __str__(self):
        return self.titulo

    @property
    def link(self):
        if self.botao_link:
            return self.botao_link
        if self.vaga_id:
            return self.vaga.get_absolute_url()
        if self.anexo:
            return self.anexo.url
        return ""

    @property
    def tipo_nome(self):
        return self.get_tipo_display().split(" ", 1)[-1]

    @property
    def chave_cliente(self):
        return f"aviso-{self.pk}-{int(self.atualizado_em.timestamp())}"

    @classmethod
    def vigentes(cls):
        agora = timezone.now()
        return (cls.objects.filter(ativo=True, inicio__lte=agora)
                .filter(models.Q(fim__isnull=True) | models.Q(fim__gte=agora))
                .select_related("vaga"))


# --------------------------------------------------------------------------- Unidades
class Unidade(Ordenavel):
    STATUS = [("ativa", "Em operação"), ("implantacao", "Em implantação")]

    nome = models.CharField("cidade / nome", max_length=120)
    uf = models.CharField("UF", max_length=2, default="BA")
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    status = models.CharField("situação", max_length=12, choices=STATUS, default="ativa")
    sede = models.BooleanField("é a sede/escritório", default=False)
    resumo = models.CharField("resumo", max_length=300)
    descricao = models.TextField("descrição completa", blank=True)
    endereco = models.CharField("endereço", max_length=300, blank=True)
    telefone = models.CharField("telefone", max_length=40, blank=True)
    imagem = models.ImageField("foto", upload_to="unidades/", blank=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "unidade"
        verbose_name_plural = "📍 Unidades"

    def __str__(self):
        return f"{self.nome} - {self.uf}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.nome}-{self.uf}")
            slug, n = base, 2
            while Unidade.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:unidade", args=[self.slug])


# --------------------------------------------------------------------------- Vagas
class Vaga(Ordenavel):
    REGIMES = [
        ("clt", "CLT"),
        ("temporario", "Temporário"),
        ("estagio", "Estágio"),
        ("jovem-aprendiz", "Jovem aprendiz"),
        ("pj", "PJ / Prestador"),
        ("cadastro-reserva", "Cadastro reserva"),
    ]
    titulo = models.CharField("cargo", max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    unidade = models.ForeignKey(Unidade, verbose_name="unidade", null=True, blank=True,
                                on_delete=models.SET_NULL, related_name="vagas")
    local = models.CharField("local (se não houver unidade)", max_length=120, blank=True)
    regime = models.CharField("regime", max_length=20, choices=REGIMES, default="clt")
    quantidade = models.PositiveIntegerField("nº de vagas", default=1)
    salario = models.CharField("salário / benefícios", max_length=160, blank=True)
    resumo = models.CharField("resumo", max_length=300)
    descricao = models.TextField("atividades", blank=True)
    requisitos = models.TextField("requisitos", blank=True, help_text="Um por linha.")
    edital = models.FileField("edital / anexo", upload_to="vagas/", blank=True,
                              validators=[DOC_VALIDATOR])
    prazo = models.DateField("inscrições até", null=True, blank=True)
    destaque = models.BooleanField("destacar na página inicial", default=True)
    link_externo = models.URLField("link externo de inscrição", blank=True,
                                   help_text="Opcional. Se vazio, usa o formulário do site.")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "vaga"
        verbose_name_plural = "💼 Vagas de emprego"

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo)[:150] or "vaga"
            slug, n = base, 2
            while Vaga.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:vaga", args=[self.slug])

    @property
    def local_exibicao(self):
        return str(self.unidade) if self.unidade else (self.local or "A definir")

    @property
    def aberta(self):
        return self.ativo and (not self.prazo or self.prazo >= timezone.localdate())

    @property
    def lista_requisitos(self):
        return [i.strip(" -•;") for i in self.requisitos.splitlines() if i.strip()]

    @classmethod
    def abertas(cls):
        hoje = timezone.localdate()
        return (cls.objects.filter(ativo=True)
                .filter(models.Q(prazo__isnull=True) | models.Q(prazo__gte=hoje))
                .select_related("unidade"))


# --------------------------------------------------------------------------- Conteúdo extra
class Servico(Ordenavel):
    ICONES = [
        ("admin", "Administração"),
        ("gestao", "Gestão / gráfico"),
        ("equipe", "Equipe / pessoas"),
        ("limpeza", "Limpeza / conservação"),
        ("seguranca", "Segurança"),
        ("manutencao", "Manutenção"),
        ("escritorio", "Escritório / apoio"),
        ("transporte", "Transporte"),
    ]
    titulo = models.CharField("título", max_length=120)
    resumo = models.CharField("resumo", max_length=200)
    descricao = models.TextField("descrição", blank=True)
    icone = models.CharField("ícone", max_length=20, choices=ICONES, default="admin")
    imagem = models.ImageField("imagem (opcional)", upload_to="servicos/", blank=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "serviço"
        verbose_name_plural = "🛎️ Serviços"

    def __str__(self):
        return self.titulo


class Numero(Ordenavel):
    """Contadores animados (ex.: 10 anos de história)."""

    valor = models.PositiveIntegerField("número")
    prefixo = models.CharField(max_length=10, blank=True)
    sufixo = models.CharField(max_length=10, blank=True, help_text="Ex.: +, %, mil")
    rotulo = models.CharField("legenda", max_length=80)

    class Meta(Ordenavel.Meta):
        verbose_name = "número em destaque"
        verbose_name_plural = "📈 Números em destaque"

    def __str__(self):
        return f"{self.prefixo}{self.valor}{self.sufixo} {self.rotulo}"


class SlideHero(Ordenavel):
    """Imagens de fundo do banner principal (trocam automaticamente)."""

    imagem = models.ImageField("imagem de fundo", upload_to="banner/")
    legenda = models.CharField("descrição da imagem", max_length=160, blank=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "imagem do banner"
        verbose_name_plural = "🖼️ Banner principal (imagens)"

    def __str__(self):
        return self.legenda or f"Imagem {self.pk}"


class ImagemGaleria(Ordenavel):
    imagem = models.ImageField("imagem", upload_to="galeria/")
    titulo = models.CharField("legenda", max_length=160, blank=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "imagem da galeria"
        verbose_name_plural = "📷 Galeria de fotos"

    def __str__(self):
        return self.titulo or f"Imagem {self.pk}"


class Noticia(models.Model):
    titulo = models.CharField("título", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    capa = models.ImageField("imagem de capa", upload_to="noticias/", blank=True)
    resumo = models.CharField("resumo", max_length=300)
    conteudo = models.TextField("conteúdo", help_text="Linha em branco separa parágrafos.")
    publicado = models.BooleanField("publicado", default=True)
    data = models.DateTimeField("data de publicação", default=timezone.now)

    class Meta:
        verbose_name = "notícia"
        verbose_name_plural = "📰 Notícias"
        ordering = ["-data"]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo)[:200] or "noticia"
            slug, n = base, 2
            while Noticia.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:noticia", args=[self.slug])


class Documento(Ordenavel):
    CATEGORIAS = [
        ("edital", "Edital / Processo seletivo"),
        ("etica", "Códigos e políticas"),
        ("outros", "Outros"),
    ]
    titulo = models.CharField("título", max_length=160)
    categoria = models.CharField("categoria", max_length=10, choices=CATEGORIAS, default="edital")
    arquivo = models.FileField("arquivo", upload_to="documentos/", blank=True, validators=[DOC_VALIDATOR])
    link = models.URLField("ou link externo", blank=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "documento"
        verbose_name_plural = "📄 Documentos (editais, códigos)"

    def __str__(self):
        return self.titulo

    @property
    def url(self):
        return self.arquivo.url if self.arquivo else (self.link or "#")


# --------------------------------------------------------------------------- Formulários recebidos
class MensagemContato(models.Model):
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    telefone = models.CharField(max_length=40, blank=True)
    assunto = models.CharField(max_length=160, blank=True)
    mensagem = models.TextField()
    lida = models.BooleanField("lida", default=False)
    criado_em = models.DateTimeField("recebida em", auto_now_add=True)

    class Meta:
        verbose_name = "mensagem de contato"
        verbose_name_plural = "✉️ Mensagens de contato"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} — {self.assunto or self.mensagem[:40]}"


class Candidatura(models.Model):
    STATUS = [
        ("nova", "Nova"),
        ("analise", "Em análise"),
        ("entrevista", "Entrevista"),
        ("aprovada", "Aprovada"),
        ("reprovada", "Não selecionada"),
    ]
    vaga = models.ForeignKey(Vaga, verbose_name="vaga", null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="candidaturas")
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    telefone = models.CharField(max_length=40)
    cidade = models.CharField(max_length=120, blank=True)
    curriculo = models.FileField(
        "currículo", upload_to="curriculos/%Y/%m/",
        validators=[FileExtensionValidator(["pdf", "doc", "docx", "odt"])], blank=True)
    mensagem = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="nova")
    observacoes = models.TextField("observações internas", blank=True)
    criado_em = models.DateTimeField("enviada em", auto_now_add=True)

    class Meta:
        verbose_name = "candidatura"
        verbose_name_plural = "🪪 Candidaturas recebidas"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} → {self.vaga or 'Banco de talentos'}"


def gerar_protocolo():
    return timezone.now().strftime("%Y%m") + "-" + secrets.token_hex(3).upper()


class Denuncia(models.Model):
    CATEGORIAS = [
        ("conduta", "Conduta antiética"),
        ("assedio", "Assédio moral ou sexual"),
        ("discriminacao", "Discriminação"),
        ("fraude", "Fraude / corrupção"),
        ("seguranca", "Segurança do trabalho"),
        ("outros", "Outros"),
    ]
    STATUS = [("recebida", "Recebida"), ("apuracao", "Em apuração"), ("concluida", "Concluída")]
    protocolo = models.CharField(max_length=20, unique=True, default=gerar_protocolo, editable=False)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="conduta")
    relato = models.TextField()
    anonima = models.BooleanField("anônima", default=True)
    nome = models.CharField(max_length=120, blank=True)
    contato = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="recebida")
    resposta = models.TextField("resposta ao denunciante", blank=True,
                                help_text="Aparece para quem consultar o protocolo.")
    criado_em = models.DateTimeField("recebida em", auto_now_add=True)

    class Meta:
        verbose_name = "denúncia"
        verbose_name_plural = "🛡️ Canal de denúncias"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"#{self.protocolo} — {self.get_categoria_display()}"
