"""Popula o banco com o conteúdo do site original (gnnordeste.com.br).

    python manage.py popular_site               # conteúdo + exemplos de vagas/avisos/notícias
    python manage.py popular_site --sem-exemplos
    python manage.py popular_site --resetar     # apaga o conteúdo editável antes

Só cria o que ainda não existe, então pode rodar de novo sem duplicar.
"""
from datetime import timedelta
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from core import models as m

SEED = Path(__file__).resolve().parents[2] / "seed"


def arquivo(rel):
    p = SEED / rel
    return File(p.open("rb"), name=p.name) if p.exists() else None


def com_arquivo(obj, campo, rel):
    f = arquivo(rel)
    if f:
        with f:
            getattr(obj, campo).save(f.name, f, save=False)
    return obj


SECOES = [
    # chave, página, nome, campos
    ("home_hero", "home", "Banner principal", dict(
        sobretitulo="Administração e Gerenciamento",
        titulo="Excelência em Terceirização de Serviços em Todo o Brasil",
        destaque="Terceirização de Serviços",
        texto="Com uma equipe capacitada e serviços personalizados, atendemos às necessidades de nossos "
              "parceiros em todo o território nacional, garantindo satisfação e renovações contratuais contínuas.",
        itens="Setor público e privado\nEquipe capacitada\nAtuação nacional",
        botao_texto="Saiba mais", botao_link="/quem-somos/", imagem="img/profissional.png")),
    ("home_sobre", "home", "Nosso Grupo", dict(
        sobretitulo="Nosso Grupo",
        titulo="Como o Grupo Nordeste se tornou o parceiro de confiança de tantas empresas?",
        destaque="parceiro de confiança",
        texto="O Grupo Nordeste se tornou o parceiro de confiança de tantas empresas devido ao seu compromisso "
              "com a excelência, sua capacidade de oferecer serviços de alta qualidade de forma consistente e sua "
              "equipe altamente capacitada e dedicada. Sua abordagem personalizada e foco nas necessidades "
              "específicas de cada cliente garantem uma parceria sólida e duradoura.",
        itens="Dedicação à excelência\nQualidade consistente nos serviços prestados\nEquipe capacitada e dedicada",
        botao_texto="Conheça nossa história", botao_link="/quem-somos/", imagem="img/equipe-grupo.jpg")),
    ("home_servicos", "home", "Nossos Serviços", dict(
        sobretitulo="Nossos Serviços",
        titulo="Explorando Possibilidades: Nossos Serviços Sob Medida",
        destaque="Sob Medida",
        subtitulo="Soluções completas para que sua organização foque no que realmente importa.")),
    ("home_unidades", "home", "Unidades (prévia)", dict(
        sobretitulo="Onde estamos",
        titulo="Presença forte na Bahia e no Centro-Oeste",
        destaque="Presença forte",
        subtitulo="Unidades em operação e novas unidades em implantação, levando excelência em terceirização "
                  "para cada vez mais cidades.")),
    ("home_trabalhe", "home", "Trabalhe Conosco", dict(
        sobretitulo="Trabalhe Conosco",
        titulo="Faça parte de nossa equipe!",
        destaque="nossa equipe",
        texto="Buscamos profissionais comprometidos e talentosos que desejam fazer a diferença, trabalhando em um "
              "ambiente dinâmico e colaborativo. Junte-se a nós e seja parte de uma organização comprometida com "
              "a excelência e o crescimento.",
        imagem="img/hero-reuniao.jpg")),
    ("home_contato", "home", "Contato", dict(
        sobretitulo="Contato",
        titulo="Fale com a nossa equipe",
        destaque="nossa equipe",
        texto="O Grupo Nordeste zela pela comunicação transparente e, por aqui, é possível tirar todas as suas "
              "dúvidas sobre nossos serviços, além de solicitar orçamentos.")),
    ("home_integridade", "home", "Canal de denúncias", dict(
        titulo="Canal de denúncias",
        texto="Em compromisso com a transparência, integridade e ética, disponibilizamos este canal de denúncias "
              "para relatar e acompanhar irregularidades relacionadas ao Grupo Nordeste. Sua contribuição é "
              "essencial para mantermos um ambiente seguro e responsável.",
        botao_texto="Fazer uma denúncia")),
    ("cta_final", "home", "Chamada final (todas as páginas internas)", dict(
        titulo="Vamos construir uma parceria de sucesso?",
        destaque="parceria de sucesso",
        subtitulo="Fale com nossa equipe e descubra como o Grupo Nordeste pode atender às suas demandas.",
        botao_texto="Solicitar orçamento", botao_link="/contato/")),
    ("qs_hero", "quem-somos", "Topo", dict(
        sobretitulo="Quem somos", titulo="Quem somos",
        subtitulo="Soluções personalizadas e de alta qualidade, com uma equipe comprometida com a excelência e "
                  "satisfação do cliente.", imagem="img/predios.jpg")),
    ("qs_historia", "quem-somos", "Nossa história", dict(
        sobretitulo="Nossa história",
        titulo="Referência em terceirização de serviços há mais de uma década",
        destaque="mais de uma década",
        texto="Bem-vindo ao Grupo Nordeste, uma referência em terceirização de serviços com mais de uma década de "
              "experiência no mercado. Desde nossa fundação, temos nos destacado pela excelência e compromisso com a "
              "satisfação do cliente, seja no setor público ou privado. Nossa equipe altamente qualificada e dedicada "
              "está empenhada em oferecer soluções personalizadas e de alta qualidade, atendendo as demandas "
              "específicas de cada cliente em todo o território nacional.\n\n"
              "No âmbito do gerenciamento de serviços, nossa abordagem meticulosa e proativa nos permite compreender "
              "profundamente as necessidades dos nossos parceiros, resultando em uma gestão inteligente e eficiente "
              "que supera expectativas. Além disso, estamos constantemente em busca de inovação e melhoria, utilizando "
              "um processo de pesquisa contínua para identificar oportunidades e garantir a entrega de serviços que "
              "se destacam pela qualidade e eficácia.\n\n"
              "Na área de terceirização de mão de obra, oferecemos uma solução eficaz para empresas que desejam "
              "otimizar recursos e focar em suas atividades principais. Nossa equipe, devidamente treinada e "
              "qualificada, assegura a máxima qualidade e agilidade na execução das tarefas, permitindo que nossos "
              "clientes concentrem seus esforços em áreas estratégicas de crescimento e desenvolvimento.",
        imagem="img/quem-somos.jpg")),
    ("qs_valores", "quem-somos", "Nossos valores", dict(
        sobretitulo="No que acreditamos", titulo="Valores que guiam o Grupo Nordeste", destaque="Grupo Nordeste",
        subtitulo="Faça parte da nossa equipe e junte-se a nós em nossa missão de proporcionar excelência e "
                  "satisfação em todos os serviços que oferecemos.",
        itens="Valorizamos a diversidade\nProfissionalismo em cada entrega\nCompromisso com a qualidade\n"
              "Superar as expectativas de clientes e parceiros")),
    ("qs_atuacao", "quem-somos", "Áreas de atuação", dict(
        sobretitulo="Áreas de atuação", titulo="O que fazemos de melhor", destaque="de melhor")),
    ("un_hero", "unidades", "Topo", dict(
        sobretitulo="Nossa presença", titulo="Unidades",
        subtitulo="Conheça as cidades onde o Grupo Nordeste atua com excelência em terceirização de serviços.",
        imagem="img/predios.jpg")),
    ("un_implantacao", "unidades", "Novas unidades", dict(
        sobretitulo="Expansão", titulo="Novas Unidades em Implantação!", destaque="Implantação",
        texto="O Grupo Nordeste está em expansão! Em breve, novas unidades estarão em funcionamento, ampliando nossa "
              "presença e reforçando nosso compromisso com a excelência na prestação de serviços.\n\n"
              "Acompanhe nossas atualizações e fique por dentro das novidades!")),
    ("tc_hero", "trabalhe-conosco", "Topo", dict(
        sobretitulo="Trabalhe Conosco", titulo="Cadastre o seu currículo", destaque="currículo",
        subtitulo="Junte-se a nós em nossa missão de proporcionar excelência e satisfação em todos os serviços que "
                  "oferecemos.", imagem="img/equipe-escritorio.jpg")),
    ("tc_form", "trabalhe-conosco", "Formulário de currículo", dict(
        sobretitulo="Banco de talentos", titulo="Faça parte de nossa equipe", destaque="nossa equipe",
        texto="Não se esqueça de anexar seu currículo à mensagem. É a chave para garantir sua candidatura de forma "
              "completa e eficiente.",
        itens="Escolha a vaga ou o banco de talentos\nPreencha seus dados e anexe o currículo\n"
              "Nossa equipe de RH entra em contato")),
    ("ct_hero", "contato", "Topo", dict(
        sobretitulo="Contato", titulo="Entre em contato com a nossa equipe", destaque="nossa equipe",
        subtitulo="Estamos disponíveis para fornecer mais informações, esclarecer dúvidas e iniciar uma parceria "
                  "de sucesso.", imagem="img/equipe-escritorio.jpg")),
    ("nt_hero", "noticias", "Topo", dict(
        sobretitulo="Notícias", titulo="Novidades do Grupo Nordeste", destaque="Grupo Nordeste",
        subtitulo="Acompanhe comunicados, processos seletivos e a expansão das nossas unidades.",
        imagem="img/predios.jpg")),
    ("dn_hero", "denuncias", "Topo", dict(
        sobretitulo="Integridade", titulo="Canal de denúncias", destaque="denúncias",
        subtitulo="Transparência, integridade e ética em todas as nossas relações.", imagem="img/predios.jpg")),
    ("dn_info", "denuncias", "Como funciona", dict(
        sobretitulo="Como funciona", titulo="Sua voz é essencial", destaque="essencial",
        texto="Em compromisso com a transparência, integridade e ética, disponibilizamos este canal de denúncias para "
              "relatar e acompanhar irregularidades relacionadas ao Grupo Nordeste. Sua contribuição é essencial "
              "para mantermos um ambiente seguro e responsável.",
        itens="Você pode se identificar ou permanecer anônimo\nCada relato gera um número de protocolo\n"
              "Acompanhe o andamento a qualquer momento")),
]

SERVICOS = [
    ("Administração de Serviços", "Comunicação aberta, transparente e eficaz.", "admin",
     "Administramos contratos e equipes com transparência, relatórios claros e um canal de comunicação direto "
     "com o cliente."),
    ("Gerenciamento de Serviços", "Gestão profissional, inteligente e eficiente.", "gestao",
     "Abordagem meticulosa e proativa para compreender as necessidades de cada parceiro, com gestão inteligente "
     "e melhoria contínua."),
    ("Terceirização de Mão de Obra", "Foco na otimização de recursos e atividades principais.", "equipe",
     "Equipes treinadas e qualificadas, garantindo qualidade e agilidade para que o cliente foque em suas áreas "
     "estratégicas."),
]

NUMEROS = [(10, "+", "anos de história"), (16, "", "unidades em operação"),
           (3, "", "novas unidades em implantação"), (2, "", "estados atendidos")]

UNIDADES = [
    # nome, uf, status, sede, resumo, imagem
    ("Escritório Salvador Trade Center", "BA", "ativa", True,
     "Avenida Tancredo Neves n.º 1632, SL 312 e 313, Torre Norte. Edifício Salvador Trade Center, Caminho das "
     "Árvores, Salvador – BA.", "salvador"),
    ("Cravolândia", "BA", "ativa", False,
     "Em Cravolândia, nossa atuação fortalece as raízes locais com compromisso social e crescimento sustentável.",
     "cravolandia"),
    ("Esplanada", "BA", "ativa", False,
     "Em Esplanada, unimos tradição e progresso para construir um futuro melhor com excelência e dedicação.",
     "esplanada"),
    ("Camamu", "BA", "ativa", False,
     "Atendendo com excelência no coração do baixo sul da Bahia, com serviços de terceirização com qualidade, "
     "agilidade e confiança.", "camamu"),
    ("Campo Alegre de Lourdes", "BA", "ativa", False,
     "Levando profissionalismo e soluções eficientes em terceirização, nossa unidade em Campo Alegre de Lourdes.",
     "campo-alegre-de-lourdes"),
    ("Firmino Alves", "BA", "ativa", False,
     "Nossa unidade em Firmino Alves atua com dedicação e profissionalismo, oferecendo soluções de terceirização.",
     "firmino-alves"),
    ("Várzea da Roça", "BA", "ativa", False,
     "Com profissionalismo e eficiência, nossa unidade em Várzea da Roça garante soluções em terceirização que "
     "geram resultados confiáveis.", "varzea-da-roca"),
    ("São João Batista", "BA", "ativa", False,
     "Em São João Batista, o Grupo Nordeste está presente com serviços de terceirização que priorizam segurança, "
     "agilidade e eficiência.", "sao-joao-batista"),
    ("Trindade", "GO", "ativa", False,
     "Somos parte do desenvolvimento goiano, com inovação, responsabilidade e presença forte no Centro-Oeste.",
     "trindade"),
    ("Antonio Gonçalves", "BA", "ativa", False,
     "Estamos lado a lado com a comunidade, promovendo transformação e novas oportunidades.", "antonio-goncalves"),
    ("Alcobaça", "BA", "ativa", False,
     "Nossa unidade em Alcobaça está pronta para oferecer qualidade, segurança e profissionalismo.", "alcobaca"),
    ("Cachoeirinha", "BA", "ativa", False,
     "Com foco em eficiência e comprometimento, nossa unidade em Cachoeirinha oferece soluções de terceirização.",
     "cachoeirinha"),
    ("Caravelas", "BA", "ativa", False,
     "Com compromisso e excelência, oferecemos serviços de terceirização que garantem eficiência, qualidade e "
     "confiança.", "caravelas"),
    ("Morpará", "BA", "ativa", False,
     "Em Morpará, o Grupo Nordeste está presente com soluções em terceirização que unem qualidade, confiança e "
     "eficiência.", "morpara"),
    ("Vitória da Conquista", "BA", "ativa", False,
     "Em um dos maiores polos do sudoeste baiano, nossa unidade em Vitória da Conquista oferece excelência em "
     "terceirização.", "vitoria-da-conquista"),
    ("Terra Nova", "BA", "ativa", False,
     "Com atendimento próximo e soluções de confiança, nossa unidade em Terra Nova oferece terceirização de "
     "qualidade.", "terra-nova"),
    ("Santo Amaro", "BA", "implantacao", False,
     "Estamos chegando a Santo Amaro para oferecer soluções estratégicas e eficientes em terceirização de serviços. "
     "Em breve, nossa unidade estará pronta para atender com excelência as demandas do setor público e privado na "
     "região!", "santo-amaro"),
    ("Uauá", "BA", "implantacao", False,
     "Nossa expansão chega a Uauá! Em breve, estaremos presentes na região, garantindo soluções personalizadas e "
     "eficientes para empresas e órgãos públicos. Fique ligado nas novidades!", "uaua"),
    ("Itaparica", "BA", "implantacao", False,
     "O Grupo Nordeste está expandindo sua atuação para Itaparica! Em breve, nossa nova unidade estará em "
     "funcionamento, proporcionando serviços de alta qualidade e contribuindo para o desenvolvimento local.",
     "itaparica"),
]


class Command(BaseCommand):
    help = "Popula o site com o conteúdo original do Grupo Nordeste."

    def add_arguments(self, parser):
        parser.add_argument("--sem-exemplos", action="store_true",
                            help="Não cria vagas, avisos e notícias de exemplo.")
        parser.add_argument("--resetar", action="store_true",
                            help="Apaga seções, unidades, serviços, números, avisos, vagas, notícias e imagens antes.")

    def handle(self, *args, **opts):
        if opts["resetar"]:
            for model in (m.Secao, m.Unidade, m.Servico, m.Numero, m.Aviso, m.Vaga, m.Noticia, m.SlideHero,
                          m.ImagemGaleria, m.Documento):
                model.objects.all().delete()

        m.ConfiguracaoSite.carregar()

        for chave, pagina, nome, campos in SECOES:
            if m.Secao.objects.filter(chave=chave).exists():
                continue
            campos = dict(campos)
            img = campos.pop("imagem", None)
            s = m.Secao(chave=chave, pagina=pagina, nome=nome, **campos)
            if img:
                com_arquivo(s, "imagem", img)
            s.save()

        if not m.Servico.objects.exists():
            for i, (t, r, ic, d) in enumerate(SERVICOS):
                m.Servico.objects.create(titulo=t, resumo=r, icone=ic, descricao=d, ordem=i)

        if not m.Numero.objects.exists():
            for i, (v, suf, rot) in enumerate(NUMEROS):
                m.Numero.objects.create(valor=v, sufixo=suf, rotulo=rot, ordem=i)

        if not m.Unidade.objects.exists():
            for i, (nome, uf, status, sede, resumo, img) in enumerate(UNIDADES):
                u = m.Unidade(nome=nome, uf=uf, status=status, sede=sede, resumo=resumo, ordem=i,
                              endereco=resumo if sede else "")
                com_arquivo(u, "imagem", f"img/unidades/{img}.jpg").save()

        if not m.SlideHero.objects.exists():
            for i, (img, leg) in enumerate([("hero-reuniao", "Reunião de equipe"),
                                            ("equipe-escritorio", "Equipe no escritório"),
                                            ("predios", "Centro empresarial")]):
                com_arquivo(m.SlideHero(legenda=leg, ordem=i), "imagem", f"img/{img}.jpg").save()

        if not m.ImagemGaleria.objects.exists():
            for i, (img, leg) in enumerate([("galeria-1", "Planejamento"), ("galeria-2", "Gestão de equipes"),
                                            ("galeria-3", "Atendimento ao cliente"), ("equipe-grupo", "Treinamentos"),
                                            ("equipe-escritorio", "Colaboração"), ("hero-reuniao", "Reuniões")]):
                com_arquivo(m.ImagemGaleria(titulo=leg, ordem=i), "imagem", f"img/{img}.jpg").save()

        if not m.Documento.objects.exists():
            com_arquivo(m.Documento(titulo="Acesse o Edital", categoria="edital", ordem=0),
                        "arquivo", "docs/Processo-Seletivo-ficha-de-inscricao.pdf").save()
            com_arquivo(m.Documento(titulo="Edital de Convocação", categoria="edital", ordem=1),
                        "arquivo", "docs/EDITAL-DE-CONVOCACAO-0001-1.pdf").save()
            # O site original lista estes documentos, mas sem arquivo. Ficam ocultos até o PDF ser enviado.
            m.Documento.objects.create(titulo="Código de Ética e Conduta", categoria="etica", ordem=2, ativo=False)
            m.Documento.objects.create(titulo="Código de Ética e Conduta de Terceiros", categoria="etica", ordem=3,
                                       ativo=False)

        if not opts["sem_exemplos"]:
            self._exemplos()

        self.stdout.write(self.style.SUCCESS("Conteúdo do Grupo Nordeste carregado."))

    def _exemplos(self):
        if m.Vaga.objects.exists():
            return
        hoje = timezone.localdate()
        u = {x.nome: x for x in m.Unidade.objects.all()}
        edital = m.Documento.objects.filter(titulo="Edital de Convocação").first()
        v1 = m.Vaga.objects.create(
            titulo="Auxiliar de Serviços Gerais", unidade=u.get("Vitória da Conquista"), regime="clt", quantidade=12,
            resumo="Limpeza e conservação de ambientes internos e externos em órgãos públicos atendidos pelo grupo.",
            descricao="Executar a limpeza e conservação de ambientes.\n\nOrganizar materiais e zelar pelos "
                      "equipamentos de trabalho.",
            requisitos="Ensino fundamental completo\nDisponibilidade de horário\nResidir na região",
            salario="Salário compatível + vale-transporte + vale-alimentação",
            prazo=hoje + timedelta(days=20), ordem=0)
        if edital and edital.arquivo:
            v1.edital.name = edital.arquivo.name
            v1.save()
        m.Vaga.objects.create(
            titulo="Recepcionista", unidade=u.get("Escritório Salvador Trade Center"), regime="clt", quantidade=2,
            resumo="Atendimento ao público, controle de agenda e apoio administrativo.",
            requisitos="Ensino médio completo\nBoa comunicação\nConhecimentos básicos de informática",
            prazo=hoje + timedelta(days=15), ordem=1)
        m.Vaga.objects.create(
            titulo="Porteiro / Controlador de Acesso", unidade=u.get("Trindade"), regime="clt", quantidade=4,
            resumo="Controle de entrada e saída de pessoas e veículos, com atenção às normas de segurança.",
            requisitos="Ensino médio completo\nExperiência na função será um diferencial",
            prazo=hoje + timedelta(days=25), ordem=2)

        com_arquivo(m.Aviso(
            tipo="contratacao", formato="modal", local="home", vaga=v1, frequencia="sessao",
            titulo="Estamos contratando em Vitória da Conquista!",
            texto="Processo seletivo aberto para Auxiliar de Serviços Gerais. Inscreva-se pelo site e anexe seu "
                  "currículo.", botao_texto="Quero me candidatar"), "imagem", "img/galeria-3.jpg").save()
        m.Aviso.objects.create(
            tipo="edital", formato="secao", local="home", ordem=0,
            titulo="Edital de Convocação disponível",
            texto="Candidatos aprovados no processo seletivo: confira o edital de convocação e a documentação "
                  "necessária.", botao_texto="Ver vagas", botao_link="/trabalhe-conosco/",
            anexo=edital.arquivo.name if edital else "")
        m.Aviso.objects.create(
            tipo="contratacao", formato="faixa", local="todas",
            titulo="Processo seletivo aberto", texto="Vagas para diversas unidades na Bahia e em Goiás.",
            botao_texto="Ver vagas", botao_link="/trabalhe-conosco/")
        m.Aviso.objects.create(
            tipo="informativo", formato="secao", local="unidades",
            titulo="Novas unidades a caminho",
            texto="Santo Amaro, Uauá e Itaparica estão em implantação. Quer trabalhar nessas cidades? Cadastre-se no "
                  "banco de talentos.", botao_texto="Cadastrar currículo", botao_link="/trabalhe-conosco/#candidatura")

        if not m.Noticia.objects.exists():
            n = m.Noticia(
                titulo="Grupo Nordeste anuncia novas unidades em Santo Amaro, Uauá e Itaparica",
                resumo="A expansão amplia a presença do grupo na Bahia e reforça o compromisso com a excelência "
                       "na prestação de serviços.",
                conteudo="O Grupo Nordeste está em expansão! Em breve, novas unidades estarão em funcionamento em "
                         "Santo Amaro, Uauá e Itaparica, ampliando nossa presença e reforçando nosso compromisso com "
                         "a excelência na prestação de serviços.\n\nAs novas unidades vão atender demandas do setor "
                         "público e privado com soluções personalizadas e eficientes.\n\nAcompanhe nossas "
                         "atualizações e fique por dentro das novidades!")
            com_arquivo(n, "capa", "img/unidades/itaparica.jpg").save()
            n = m.Noticia(
                titulo="Processo seletivo: edital de convocação publicado",
                resumo="Candidatos devem conferir o edital e a ficha de inscrição na página Trabalhe Conosco.",
                conteudo="O edital de convocação do processo seletivo está disponível para download na página "
                         "Trabalhe Conosco, junto com a ficha de inscrição.\n\nNão se esqueça de anexar seu "
                         "currículo ao se candidatar.",
                data=timezone.now() - timedelta(days=3))
            com_arquivo(n, "capa", "img/equipe-escritorio.jpg").save()
