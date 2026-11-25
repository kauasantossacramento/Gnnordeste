import io
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from .models import Aviso, Candidatura, Configuracao, Mensagem, Proposta, Secao, Servico, Vaga

MEDIA = tempfile.mkdtemp()


def png():
    buf = io.BytesIO()
    Image.new("RGBA", (20, 20), (36, 72, 61, 255)).save(buf, "PNG")
    return SimpleUploadedFile("logo-nova.png", buf.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=MEDIA)
class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("popular_site", verbosity=0)
        User.objects.create_superuser("admin", "a@a.com", "senha-teste-123")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def test_paginas_publicas(self):
        urls = ["/", "/a-empresa/", "/servicos/", Servico.objects.first().get_absolute_url(), "/monte-sua-equipe/",
                "/carreiras/", Vaga.objects.first().get_absolute_url(), "/carreiras/acompanhar/", "/conteudos/",
                "/contato/", "/p/privacidade/", "/sitemap.xml", "/robots.txt"]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get("/nao-existe/").status_code, 404)

    # ---------------------------------------------------------------- editável pelo painel
    def test_texto_editado_no_painel_aparece_no_site(self):
        Secao.objects.filter(chave="home_hero").update(subtitulo="Texto trocado pelo painel")
        Secao.objects.filter(chave="geral_rodape").update(titulo="Rodapé novo")
        r = self.client.get("/")
        self.assertContains(r, "Texto trocado pelo painel")
        self.assertContains(r, "Rodapé novo")

    def test_secao_desativada_some(self):
        self.assertContains(self.client.get("/"), "Tire suas")
        Secao.objects.filter(chave="home_faq").update(ativo=False)
        self.assertNotContains(self.client.get("/"), "Tire suas")

    def test_logo_enviada_no_painel_substitui_a_padrao(self):
        cfg = Configuracao.carregar()
        cfg.logo = png()
        cfg.save()
        self.assertContains(self.client.get("/"), "/media/marca/logo-nova")

    def test_aviso_formatos(self):
        r = self.client.get("/")
        self.assertContains(r, 'class="modal"')
        self.assertContains(r, 'class="faixa')
        self.assertContains(r, 'class="flutuante')
        Aviso.objects.update(ativo=False)
        r = self.client.get("/")
        self.assertNotContains(r, 'class="modal"')
        self.assertNotContains(r, 'class="flutuante')

    # ---------------------------------------------------------------- formulários
    def test_monte_sua_equipe(self):
        s = list(Servico.objects.values_list("pk", flat=True)[:2])
        r = self.client.post("/monte-sua-equipe/", {
            "servicos": s, "profissionais": 30, "contrato": "continuo", "inicio": "30", "setor": "publico",
            "cidade": "Salvador", "uf": "BA", "empresa": "Prefeitura X", "nome": "Ana Souza",
            "email": "ana@x.gov.br", "telefone": "(71) 99999-0000", "aceite": "on", "perfis": "Recepcionista"},
            follow=True)
        p = Proposta.objects.get()
        self.assertEqual(p.servicos.count(), 2)
        self.assertTrue(p.protocolo.startswith("PR-"))
        self.assertContains(r, p.protocolo)
        self.assertContains(r, "Obrigado, Ana!")

    def test_proposta_sem_servico_nao_salva(self):
        self.client.post("/monte-sua-equipe/", {"profissionais": 3, "cidade": "X", "uf": "BA", "empresa": "Y",
                                                "nome": "Z", "email": "z@z.com", "telefone": "1", "aceite": "on"})
        self.assertEqual(Proposta.objects.count(), 0)

    def test_candidatura_e_acompanhamento(self):
        v = Vaga.objects.first()
        cv = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 teste", content_type="application/pdf")
        r = self.client.post(v.get_absolute_url(), {"vaga": v.pk, "nome": "Maria", "email": "m@m.com",
                                                    "telefone": "71999999999", "curriculo": cv, "aceite": "on"},
                             follow=True)
        c = Candidatura.objects.get()
        self.assertContains(r, c.protocolo)
        c.status, c.retorno = "entrevista", "Entrevista dia 10 às 9h."
        c.save()
        r = self.client.get("/carreiras/acompanhar/", {"protocolo": c.protocolo, "email": "M@M.com"})
        self.assertContains(r, "Entrevista agendada")
        self.assertContains(r, "Entrevista dia 10")
        r = self.client.get("/carreiras/acompanhar/", {"protocolo": c.protocolo, "email": "outro@x.com"})
        self.assertContains(r, "Não encontramos")

    def test_contato_e_honeypot(self):
        dados = {"nome": "Ana", "email": "a@a.com", "assunto": "duvida", "mensagem": "Olá", "aceite": "on"}
        self.client.post("/contato/", dados)
        self.client.post("/contato/", {**dados, "website": "spam"})
        self.assertEqual(Mensagem.objects.count(), 1)

    # ---------------------------------------------------------------- SEO
    def test_dados_estruturados(self):
        v = Vaga.objects.first()
        self.assertContains(self.client.get(v.get_absolute_url()), '"@type": "JobPosting"')
        self.assertContains(self.client.get("/"), '"@type": "FAQPage"')
        self.assertContains(self.client.get("/sitemap.xml"), v.get_absolute_url())

    # ---------------------------------------------------------------- painel
    def test_painel(self):
        self.client.login(username="admin", password="senha-teste-123")
        urls = ["/painel/", "/painel/core/secao/", "/painel/core/secao/1/change/", "/painel/core/aviso/",
                "/painel/core/aviso/add/", "/painel/core/vaga/", "/painel/core/vaga/1/change/",
                "/painel/core/candidatura/", "/painel/core/proposta/", "/painel/core/configuracao/1/change/",
                "/painel/core/servico/", "/painel/core/artigo/add/", "/painel/core/pagina/", "/painel/auth/user/"]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
