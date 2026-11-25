"""Conteúdo do site da Empreender Soluções.

Tudo é editável em /painel/: textos de cada seção, serviços, segmentos, vagas, avisos
(seção, modal, faixa ou flutuante), conteúdos, FAQ, páginas e dados da empresa.
Formulários do site (propostas, candidaturas e contato) também ficam salvos aqui.
"""
import secrets

from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

DOCS = FileExtensionValidator(["pdf", "doc", "docx", "odt", "jpg", "jpeg", "png"])
CV = FileExtensionValidator(["pdf", "doc", "docx", "odt"])

UFS = [(u, u) for u in "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()]


def slug_unico(obj, texto, campo="slug", limite=150):
    base = slugify(texto)[:limite] or "item"
    slug, n = base, 2
    while type(obj).objects.filter(**{campo: slug}).exclude(pk=obj.pk).exists():
        slug, n = f"{base}-{n}", n + 1
    return slug


def protocolo(prefixo):
    return f"{prefixo}-{timezone.now():%y%m}-{secrets.token_hex(3).upper()}"


def linhas(texto):
    return [i.strip(" -•;") for i in (texto or "").splitlines() if i.strip()]


class Ordenavel(models.Model):
    ordem = models.PositiveIntegerField("ordem", default=0, help_text="Menor aparece primeiro.")
    ativo = models.BooleanField("visível no site", default=True)

    class Meta:
        abstract = True
        ordering = ["ordem", "id"]


# ============================================================================ Empresa
class Configuracao(models.Model):
    nome = models.CharField("nome", max_length=120, default="Empreender Soluções")
    slogan = models.CharField("slogan", max_length=200,
                              default="Conectar estratégias. Estruturar soluções. Impulsionar o desenvolvimento.")
    descricao_curta = models.CharField(
        "descrição curta (rodapé)", max_length=300,
        default="Mão de obra especializada e apoio administrativo para organizações públicas e privadas.")
    meta_descricao = models.CharField(
        "descrição para o Google", max_length=300,
        default="Empreender Soluções: terceirização de mão de obra, apoio administrativo e gestão de equipes "
                "para empresas e órgãos públicos. Solicite uma proposta.")
    cnpj = models.CharField("CNPJ", max_length=20, blank=True)
    telefone = models.CharField("telefone", max_length=40, blank=True)
    whatsapp = models.CharField("WhatsApp (só números, com 55 + DDD)", max_length=20, blank=True,
                                help_text="Ex.: 5571999999999. Mostra o botão flutuante do WhatsApp.")
    email = models.EmailField("e-mail público", blank=True)
    email_notificacoes = models.EmailField("e-mail que recebe os formulários", blank=True,
                                           help_text="Exige SMTP configurado no servidor.")
    endereco = models.CharField("endereço", max_length=300, blank=True)
    cidade = models.CharField("cidade", max_length=80, blank=True)
    uf = models.CharField("UF", max_length=2, choices=UFS, blank=True)
    horario = models.CharField("horário de atendimento", max_length=120, default="Segunda a sexta, das 8h às 18h")
    mapa_embed = models.URLField("link do mapa (Google Maps → Incorporar → src)", max_length=800, blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    logo = models.ImageField("logo principal (fundos claros)", upload_to="marca/", blank=True,
                             help_text="Vazio = logo do manual da marca. PNG com fundo transparente.")
    logo_negativa = models.ImageField("logo negativa (fundos escuros)", upload_to="marca/", blank=True)
    simbolo = models.ImageField("símbolo colorido", upload_to="marca/", blank=True)
    simbolo_negativo = models.ImageField("símbolo negativo (fundos escuros)", upload_to="marca/", blank=True)
    favicon = models.ImageField("ícone da aba (quadrado, PNG)", upload_to="marca/", blank=True)
    imagem_compartilhamento = models.ImageField(
        "imagem ao compartilhar o link (1200×630)", upload_to="marca/", blank=True,
        help_text="Aparece no WhatsApp, LinkedIn e redes quando alguém compartilha o site.")
    google_analytics = models.CharField("ID do Google Analytics (G-XXXX)", max_length=30, blank=True)
    texto_cookies = models.CharField(
        "aviso de cookies", max_length=300,
        default="Usamos cookies essenciais para o funcionamento do site e para entender como ele é utilizado.")
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = verbose_name_plural = "dados da empresa"

    def __str__(self):
        return "Dados da empresa"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def carregar(cls):
        return cls.objects.get_or_create(pk=1)[0]

    @property
    def telefone_link(self):
        return "".join(c for c in self.telefone if c.isdigit() or c == "+")

    @property
    def redes(self):
        return [(n, u) for n, u in (("instagram", self.instagram), ("linkedin", self.linkedin),
                                     ("facebook", self.facebook), ("youtube", self.youtube)) if u]


class Secao(models.Model):
    PAGINAS = [("home", "Início"), ("sobre", "A empresa"), ("servicos", "Serviços"), ("carreiras", "Carreiras"),
               ("proposta", "Monte sua equipe"), ("contato", "Contato"), ("conteudos", "Conteúdos"),
               ("geral", "Geral")]
    chave = models.SlugField("identificador", max_length=60, unique=True,
                             help_text="Usado pelo layout para encontrar este bloco. Não altere.")
    pagina = models.CharField("página", max_length=20, choices=PAGINAS, default="home")
    nome = models.CharField("nome do bloco", max_length=120)
    sobretitulo = models.CharField("rótulo (texto pequeno acima)", max_length=120, blank=True)
    titulo = models.CharField("título", max_length=220, blank=True)
    destaque = models.CharField("trecho do título em destaque", max_length=100, blank=True,
                                help_text="Esse trecho aparece em dourado/itálico.")
    subtitulo = models.CharField("subtítulo", max_length=320, blank=True)
    texto = models.TextField("texto", blank=True, help_text="Linha em branco separa parágrafos.")
    itens = models.TextField("lista", blank=True, help_text="Um item por linha.")
    imagem = models.ImageField("imagem", upload_to="secoes/", blank=True)
    botao_texto = models.CharField("texto do botão", max_length=60, blank=True)
    botao_link = models.CharField("link do botão", max_length=300, blank=True)
    botao2_texto = models.CharField("texto do 2º botão", max_length=60, blank=True)
    botao2_link = models.CharField("link do 2º botão", max_length=300, blank=True)
    ativo = models.BooleanField("exibir", default=True)

    class Meta:
        verbose_name = "texto de seção"
        verbose_name_plural = "textos das seções"
        ordering = ["pagina", "id"]

    def __str__(self):
        return f"{self.get_pagina_display()} · {self.nome}"

    @property
    def lista(self):
        return linhas(self.itens)


# ============================================================================ Institucional
ICONES = [
    ("equipe", "Equipe"), ("pasta", "Administrativo"), ("predio", "Facilities / predial"),
    ("limpeza", "Limpeza"), ("recepcao", "Recepção / atendimento"), ("escudo", "Portaria / segurança"),
    ("ferramenta", "Manutenção"), ("grafico", "Gestão / indicadores"), ("engrenagem", "Processos"),
    ("caminhao", "Logística"), ("saude", "Saúde"), ("escola", "Educação"), ("governo", "Setor público"),
    ("fabrica", "Indústria"), ("loja", "Comércio"), ("casa", "Condomínios"),
]


class Servico(Ordenavel):
    titulo = models.CharField("serviço", max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icone = models.CharField("ícone", max_length=20, choices=ICONES, default="equipe")
    resumo = models.CharField("resumo", max_length=220)
    descricao = models.TextField("descrição", blank=True)
    inclui = models.TextField("o que inclui", blank=True, help_text="Um item por linha.")
    perfis = models.TextField("perfis profissionais", blank=True,
                              help_text="Um por linha. Aparecem no simulador 'Monte sua equipe'.")
    imagem = models.ImageField("imagem", upload_to="servicos/", blank=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "serviço"
        verbose_name_plural = "serviços"

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        self.slug = self.slug or slug_unico(self, self.titulo)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:servico", args=[self.slug])

    @property
    def lista_inclui(self):
        return linhas(self.inclui)

    @property
    def lista_perfis(self):
        return linhas(self.perfis)


class Segmento(Ordenavel):
    titulo = models.CharField("segmento", max_length=80)
    icone = models.CharField("ícone", max_length=20, choices=ICONES, default="predio")
    texto = models.CharField("texto", max_length=200)

    class Meta(Ordenavel.Meta):
        verbose_name = "segmento atendido"
        verbose_name_plural = "segmentos atendidos"

    def __str__(self):
        return self.titulo


class Pilar(Ordenavel):
    titulo = models.CharField("pilar", max_length=60)
    texto = models.CharField("texto", max_length=200)

    class Meta(Ordenavel.Meta):
        verbose_name = "pilar da marca"
        verbose_name_plural = "pilares da marca"

    def __str__(self):
        return self.titulo


class Etapa(Ordenavel):
    titulo = models.CharField("etapa", max_length=80)
    texto = models.CharField("texto", max_length=260)

    class Meta(Ordenavel.Meta):
        verbose_name = "etapa do processo"
        verbose_name_plural = "etapas do processo"

    def __str__(self):
        return self.titulo


class Numero(Ordenavel):
    valor = models.PositiveIntegerField("número")
    prefixo = models.CharField(max_length=10, blank=True)
    sufixo = models.CharField(max_length=10, blank=True, help_text="Ex.: +, %, mil")
    rotulo = models.CharField("legenda", max_length=80)

    class Meta(Ordenavel.Meta):
        verbose_name = "número em destaque"
        verbose_name_plural = "números em destaque"

    def __str__(self):
        return f"{self.prefixo}{self.valor}{self.sufixo} {self.rotulo}"


class Pergunta(Ordenavel):
    pergunta = models.CharField("pergunta", max_length=200)
    resposta = models.TextField("resposta")

    class Meta(Ordenavel.Meta):
        verbose_name = "pergunta frequente"
        verbose_name_plural = "perguntas frequentes"

    def __str__(self):
        return self.pergunta


class Depoimento(Ordenavel):
    nome = models.CharField(max_length=80)
    cargo = models.CharField(max_length=80, blank=True)
    empresa = models.CharField(max_length=80, blank=True)
    texto = models.TextField()
    foto = models.ImageField(upload_to="depoimentos/", blank=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "depoimento"
        verbose_name_plural = "depoimentos"

    def __str__(self):
        return f"{self.nome} ({self.empresa})"


class Cliente(Ordenavel):
    nome = models.CharField(max_length=80)
    logo = models.ImageField(upload_to="clientes/")
    link = models.URLField(blank=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "cliente"
        verbose_name_plural = "clientes (logos)"

    def __str__(self):
        return self.nome


class Pagina(models.Model):
    titulo = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    conteudo = models.TextField(help_text="Linha em branco separa parágrafos. Linhas começando com ## viram subtítulos.")
    no_rodape = models.BooleanField("link no rodapé", default=True)
    publicado = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "página"
        verbose_name_plural = "páginas"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        self.slug = self.slug or slug_unico(self, self.titulo)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:pagina", args=[self.slug])


class Artigo(models.Model):
    CATEGORIAS = [("gestao", "Gestão"), ("carreiras", "Carreiras"), ("novidades", "Novidades"),
                  ("legislacao", "Legislação")]
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="novidades")
    capa = models.ImageField(upload_to="conteudos/", blank=True)
    resumo = models.CharField(max_length=300)
    conteudo = models.TextField(help_text="Linha em branco separa parágrafos. ## no começo da linha = subtítulo.")
    publicado = models.BooleanField(default=True)
    data = models.DateTimeField("data de publicação", default=timezone.now)

    class Meta:
        verbose_name = "conteúdo"
        verbose_name_plural = "conteúdos / blog"
        ordering = ["-data"]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        self.slug = self.slug or slug_unico(self, self.titulo, limite=200)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:artigo", args=[self.slug])

    @property
    def leitura(self):
        return max(1, round(len(self.conteudo.split()) / 200))


# ============================================================================ Recrutamento
class Vaga(Ordenavel):
    REGIMES = [("clt", "CLT"), ("temporario", "Temporário"), ("estagio", "Estágio"),
               ("aprendiz", "Jovem aprendiz"), ("pj", "PJ"), ("reserva", "Cadastro reserva")]
    MODALIDADES = [("presencial", "Presencial"), ("hibrido", "Híbrido"), ("remoto", "Remoto")]
    GOOGLE_REGIME = {"clt": "FULL_TIME", "temporario": "TEMPORARY", "estagio": "INTERN", "aprendiz": "INTERN",
                     "pj": "CONTRACTOR", "reserva": "OTHER"}

    titulo = models.CharField("cargo", max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    area = models.ForeignKey(Servico, verbose_name="área", null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="vagas")
    cidade = models.CharField(max_length=80)
    uf = models.CharField("UF", max_length=2, choices=UFS)
    modalidade = models.CharField(max_length=12, choices=MODALIDADES, default="presencial")
    regime = models.CharField(max_length=12, choices=REGIMES, default="clt")
    quantidade = models.PositiveIntegerField("nº de vagas", default=1)
    salario = models.CharField("salário / benefícios (resumo)", max_length=160, blank=True)
    resumo = models.CharField(max_length=300)
    descricao = models.TextField("atividades", blank=True)
    requisitos = models.TextField(blank=True, help_text="Um por linha.")
    beneficios = models.TextField("benefícios", blank=True, help_text="Um por linha.")
    edital = models.FileField("edital / anexo", upload_to="vagas/", blank=True, validators=[DOCS])
    prazo = models.DateField("inscrições até", null=True, blank=True)
    destaque = models.BooleanField("destacar na página inicial", default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "vaga"
        verbose_name_plural = "vagas"

    def __str__(self):
        return f"{self.titulo} · {self.cidade}/{self.uf}"

    def save(self, *args, **kwargs):
        self.slug = self.slug or slug_unico(self, f"{self.titulo}-{self.cidade}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:vaga", args=[self.slug])

    @property
    def local(self):
        return f"{self.cidade}/{self.uf}"

    @property
    def aberta(self):
        return self.ativo and (not self.prazo or self.prazo >= timezone.localdate())

    @property
    def nova(self):
        return (timezone.now() - self.criado_em).days <= 7

    @property
    def lista_requisitos(self):
        return linhas(self.requisitos)

    @property
    def lista_beneficios(self):
        return linhas(self.beneficios)

    @classmethod
    def abertas(cls):
        hoje = timezone.localdate()
        return (cls.objects.filter(ativo=True).filter(models.Q(prazo__isnull=True) | models.Q(prazo__gte=hoje))
                .select_related("area"))


class Candidatura(models.Model):
    STATUS = [("recebida", "Recebida"), ("triagem", "Em triagem"), ("entrevista", "Entrevista agendada"),
              ("aprovada", "Aprovada"), ("banco", "Banco de talentos"), ("encerrada", "Processo encerrado")]
    protocolo = models.CharField(max_length=20, unique=True, editable=False)
    vaga = models.ForeignKey(Vaga, null=True, blank=True, on_delete=models.SET_NULL, related_name="candidaturas")
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    telefone = models.CharField(max_length=40)
    cidade = models.CharField(max_length=120, blank=True)
    linkedin = models.URLField("LinkedIn ou portfólio", blank=True)
    curriculo = models.FileField("currículo", upload_to="curriculos/%Y/%m/", validators=[CV], blank=True)
    mensagem = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="recebida")
    retorno = models.TextField("mensagem ao candidato", blank=True,
                               help_text="Aparece para o candidato quando ele consulta o protocolo.")
    observacoes = models.TextField("anotações internas", blank=True)
    criado_em = models.DateTimeField("recebida em", auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "candidatura"
        verbose_name_plural = "candidaturas"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} → {self.vaga or 'Banco de talentos'}"

    def save(self, *args, **kwargs):
        self.protocolo = self.protocolo or protocolo("CV")
        super().save(*args, **kwargs)


# ============================================================================ Comercial
class Proposta(models.Model):
    STATUS = [("nova", "Nova"), ("contato", "Em contato"), ("enviada", "Proposta enviada"),
              ("fechada", "Contrato fechado"), ("perdida", "Não avançou")]
    PRAZOS = [("imediato", "Imediato"), ("30", "Em até 30 dias"), ("90", "Em até 3 meses"), ("avaliando", "Ainda avaliando")]
    CONTRATOS = [("continuo", "Contrato contínuo"), ("temporario", "Temporário / sazonal"), ("projeto", "Projeto pontual")]
    SETORES = [("privado", "Empresa privada"), ("publico", "Órgão público"), ("terceiro", "Terceiro setor"),
               ("condominio", "Condomínio")]

    protocolo = models.CharField(max_length=20, unique=True, editable=False)
    servicos = models.ManyToManyField(Servico, verbose_name="serviços de interesse", blank=True)
    perfis = models.CharField("perfis citados", max_length=400, blank=True)
    profissionais = models.PositiveIntegerField("nº de profissionais", default=1,
                                                validators=[MinValueValidator(1), MaxValueValidator(5000)])
    contrato = models.CharField(max_length=12, choices=CONTRATOS, default="continuo")
    inicio = models.CharField("quando precisa", max_length=10, choices=PRAZOS, default="30")
    setor = models.CharField(max_length=12, choices=SETORES, default="privado")
    cidade = models.CharField(max_length=80)
    uf = models.CharField("UF", max_length=2, choices=UFS)
    empresa = models.CharField("empresa / órgão", max_length=160)
    nome = models.CharField("responsável", max_length=120)
    cargo = models.CharField(max_length=80, blank=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=40)
    mensagem = models.TextField("detalhes", blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="nova")
    observacoes = models.TextField("anotações internas", blank=True)
    criado_em = models.DateTimeField("recebida em", auto_now_add=True)

    class Meta:
        verbose_name = "proposta solicitada"
        verbose_name_plural = "propostas (Monte sua equipe)"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.protocolo} · {self.empresa}"

    def save(self, *args, **kwargs):
        self.protocolo = self.protocolo or protocolo("PR")
        super().save(*args, **kwargs)


class Mensagem(models.Model):
    ASSUNTOS = [("proposta", "Quero contratar"), ("duvida", "Dúvida"), ("parceria", "Parceria / fornecedor"),
                ("colaborador", "Sou colaborador"), ("outro", "Outro")]
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    telefone = models.CharField(max_length=40, blank=True)
    assunto = models.CharField(max_length=12, choices=ASSUNTOS, default="duvida")
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField("recebida em", auto_now_add=True)

    class Meta:
        verbose_name = "mensagem de contato"
        verbose_name_plural = "mensagens de contato"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} · {self.get_assunto_display()}"


# ============================================================================ Avisos
class Aviso(Ordenavel):
    TIPOS = [("vagas", "Contratação / vagas"), ("edital", "Edital / processo seletivo"),
             ("informativo", "Informativo"), ("urgente", "Urgente"), ("novidade", "Novidade")]
    FORMATOS = [("secao", "Cartão dentro de uma seção"), ("modal", "Janela (modal) ao abrir a página"),
                ("faixa", "Faixa no topo do site"), ("flutuante", "Cartão flutuante no canto da tela")]
    LOCAIS = [("todas", "Todas as páginas"), ("home", "Início · abaixo do banner"),
              ("home-servicos", "Início · seção de serviços"), ("home-carreiras", "Início · seção de carreiras"),
              ("sobre", "A empresa"), ("servicos", "Serviços"), ("carreiras", "Carreiras"),
              ("proposta", "Monte sua equipe"), ("contato", "Contato"), ("conteudos", "Conteúdos")]
    FREQUENCIAS = [("sessao", "Uma vez por visita"), ("sempre", "Toda vez que abrir a página"),
                   ("uma-vez", "Uma única vez por visitante")]

    tipo = models.CharField(max_length=12, choices=TIPOS, default="vagas")
    formato = models.CharField("como exibir", max_length=10, choices=FORMATOS, default="secao")
    local = models.CharField("onde exibir", max_length=20, choices=LOCAIS, default="home")
    titulo = models.CharField(max_length=160)
    texto = models.TextField(blank=True)
    imagem = models.ImageField(upload_to="avisos/", blank=True)
    vaga = models.ForeignKey(Vaga, null=True, blank=True, on_delete=models.SET_NULL, related_name="avisos",
                             help_text="Opcional: o botão leva para a vaga e mostra cidade, regime e prazo.")
    botao_texto = models.CharField("texto do botão", max_length=60, blank=True)
    botao_link = models.CharField("link do botão", max_length=300, blank=True)
    anexo = models.FileField("anexo (PDF)", upload_to="avisos/", blank=True, validators=[DOCS])
    inicio = models.DateTimeField("exibir a partir de", default=timezone.now)
    fim = models.DateTimeField("exibir até", null=True, blank=True, help_text="Vazio = sem data para sair.")
    frequencia = models.CharField("frequência (modal e flutuante)", max_length=10, choices=FREQUENCIAS,
                                  default="sessao")
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "aviso"
        verbose_name_plural = "avisos"

    def __str__(self):
        return self.titulo

    @property
    def link(self):
        if self.botao_link:
            return self.botao_link
        if self.vaga_id:
            return self.vaga.get_absolute_url()
        return self.anexo.url if self.anexo else ""

    @property
    def chave(self):
        return f"{self.pk}-{int(self.atualizado_em.timestamp())}"

    @property
    def no_ar(self):
        agora = timezone.now()
        return self.ativo and self.inicio <= agora and (self.fim is None or self.fim >= agora)

    @classmethod
    def vigentes(cls):
        agora = timezone.now()
        return (cls.objects.filter(ativo=True, inicio__lte=agora)
                .filter(models.Q(fim__isnull=True) | models.Q(fim__gte=agora)).select_related("vaga"))
