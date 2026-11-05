import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Aviso, Candidatura, Denuncia, MensagemContato, Vaga

MEDIA = tempfile.mkdtemp()


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
        urls = ["/", "/quem-somos/", "/unidades/", "/unidades/camamu-ba/", "/trabalhe-conosco/",
                Vaga.objects.first().get_absolute_url(), "/noticias/", "/contato/", "/canal-de-denuncias/"]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get("/nao-existe/").status_code, 404)

    def test_aviso_modal_aparece_e_some_quando_inativo(self):
        r = self.client.get("/")
        self.assertContains(r, "data-modal=")
        Aviso.objects.filter(formato="modal").update(ativo=False)
        self.assertNotContains(self.client.get("/"), "data-modal=")

    def test_aviso_secao_so_no_local_escolhido(self):
        self.assertContains(self.client.get("/unidades/"), "Novas unidades a caminho")
        self.assertNotContains(self.client.get("/contato/"), "Novas unidades a caminho")

    def test_contato_e_honeypot(self):
        self.client.post("/contato/", {"nome": "Ana", "email": "a@a.com", "mensagem": "Olá"})
        self.assertEqual(MensagemContato.objects.count(), 1)
        self.client.post("/contato/", {"nome": "Bot", "email": "b@b.com", "mensagem": "x", "site": "spam"})
        self.assertEqual(MensagemContato.objects.count(), 1)

    def test_candidatura_com_curriculo(self):
        v = Vaga.objects.first()
        cv = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 teste", content_type="application/pdf")
        r = self.client.post(v.get_absolute_url(), {"vaga": v.pk, "nome": "Maria", "email": "m@m.com",
                                                    "telefone": "71999999999", "curriculo": cv, "aceite": "on"})
        self.assertEqual(r.status_code, 302)
        c = Candidatura.objects.get()
        self.assertEqual(c.vaga, v)
        self.assertTrue(c.curriculo.name.endswith(".pdf"))

    def test_candidatura_exige_lgpd(self):
        self.client.post("/trabalhe-conosco/", {"nome": "X", "email": "x@x.com", "telefone": "1"})
        self.assertEqual(Candidatura.objects.count(), 0)

    def test_denuncia_anonima_e_consulta(self):
        r = self.client.post("/canal-de-denuncias/", {"categoria": "conduta", "relato": "Relato", "anonima": "on",
                                                      "nome": "Não salvar"}, follow=True)
        d = Denuncia.objects.get()
        self.assertEqual(d.nome, "")
        self.assertContains(r, d.protocolo)
        self.assertContains(self.client.get(f"/canal-de-denuncias/?protocolo={d.protocolo}"), "Recebida")

    def test_painel(self):
        self.client.login(username="admin", password="senha-teste-123")
        for url in ["/painel/", "/painel/core/aviso/", "/painel/core/aviso/add/", "/painel/core/vaga/",
                    "/painel/core/secao/", "/painel/core/secao/1/change/", "/painel/core/configuracaosite/1/change/",
                    "/painel/core/unidade/", "/painel/core/candidatura/", "/painel/core/denuncia/",
                    "/painel/core/noticia/add/", "/painel/core/slidehero/", "/painel/core/documento/"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
