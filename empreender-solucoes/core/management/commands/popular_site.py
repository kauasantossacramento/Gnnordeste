"""Carrega o conteúdo inicial do site da Empreender Soluções.

    python manage.py popular_site                 # conteúdo + exemplos (vagas, avisos, conteúdos)
    python manage.py popular_site --sem-exemplos  # só o conteúdo institucional
    python manage.py popular_site --resetar       # apaga o conteúdo editável e recarrega

Só cria o que ainda não existe; pode rodar de novo sem duplicar.
Textos institucionais baseados no Manual da Marca (edição 2026).
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core import models as m

SECOES = [
    ("home_hero", "home", "Banner principal", dict(
        sobretitulo="Mão de obra · Apoio administrativo",
        titulo="Conectar estratégias. Estruturar soluções. Impulsionar o desenvolvimento.",
        itens="Conectar estratégias.\nEstruturar soluções.\nImpulsionar o desenvolvimento.",
        subtitulo="Montamos, gerimos e acompanhamos equipes de mão de obra e apoio administrativo para que a sua "
                  "organização foque no que move o negócio.",
        botao_texto="Monte sua equipe", botao_link="/monte-sua-equipe/",
        botao2_texto="Conheça os serviços", botao2_link="/servicos/")),
    ("home_hero_painel", "home", "Banner · painel verde e mini simulador", dict(
        sobretitulo="Soluções em", titulo="Quantos profissionais você precisa?", botao_texto="Montar proposta")),
    ("home_pilares", "home", "Pilares da marca", dict(
        sobretitulo="Como trabalhamos", titulo="Uma empresa construída sobre confiança, estratégia e evolução.",
        destaque="confiança",
        texto="Conectamos estratégias, organizamos processos e desenvolvemos soluções para a evolução dos "
              "negócios dos nossos clientes, com elementos que se complementam como as faixas do nosso símbolo.")),
    ("home_servicos", "home", "Serviços", dict(
        sobretitulo="Serviços", titulo="Soluções sob medida para cada operação", destaque="sob medida",
        subtitulo="Escolha um serviço para ver o que está incluído e os perfis profissionais disponíveis.")),
    ("home_processo", "home", "Etapas do processo", dict(
        sobretitulo="Do diagnóstico à rotina", titulo="Como estruturamos sua equipe", destaque="sua equipe",
        subtitulo="Um processo claro, do primeiro contato ao acompanhamento contínuo do contrato.")),
    ("home_segmentos", "home", "Segmentos atendidos", dict(
        sobretitulo="Para quem", titulo="Atendemos organizações públicas e privadas", destaque="públicas e privadas",
        texto="Cada segmento tem rotinas, exigências e indicadores próprios. Adaptamos perfis, escalas e "
              "processos à realidade de cada cliente.")),
    ("home_simulador", "home", "Chamada do simulador", dict(
        sobretitulo="Monte sua equipe", titulo="Diga do que precisa. Nós estruturamos o resto.",
        destaque="Nós estruturamos o resto.",
        subtitulo="Escolha os serviços e a quantidade de profissionais. Em quatro etapas, sua solicitação chega à "
                  "nossa equipe comercial.", botao_texto="Continuar")),
    ("home_carreiras", "home", "Carreiras", dict(
        sobretitulo="Carreiras", titulo="Cresça com a gente", destaque="com a gente",
        texto="Buscamos pessoas comprometidas, organizadas e que gostam de fazer bem feito. Envie seu currículo, "
              "receba um protocolo e acompanhe cada etapa da sua candidatura pelo site.",
        botao_texto="Enviar currículo", botao_link="/carreiras/#candidatura",
        botao2_texto="Acompanhar candidatura", botao2_link="/carreiras/acompanhar/")),
    ("home_faq", "home", "Perguntas frequentes", dict(
        sobretitulo="Perguntas frequentes", titulo="Tire suas dúvidas", destaque="dúvidas",
        subtitulo="Reunimos as perguntas mais comuns de quem quer contratar ou trabalhar conosco.",
        botao_texto="Outra dúvida? Fale conosco", botao_link="/contato/")),
    ("home_conteudos", "home", "Conteúdos (prévia)", dict(
        sobretitulo="Conteúdos", titulo="Gestão, carreiras e novidades", destaque="novidades",
        botao_texto="Ver todos", botao_link="/conteudos/")),
    ("home_depoimentos", "home", "Depoimentos", dict(
        sobretitulo="Depoimentos", titulo="O que dizem nossos parceiros", destaque="parceiros")),
    ("home_clientes", "home", "Clientes (logos)", dict(titulo="Quem confia na Empreender")),
    ("geral_rodape", "geral", "Chamada do rodapé (todas as páginas)", dict(
        sobretitulo="Vamos conversar", titulo="Estruture sua operação com quem entende de pessoas e processos.",
        destaque="pessoas e processos", botao_texto="Monte sua equipe", botao_link="/monte-sua-equipe/",
        botao2_texto="Fale com a gente", botao2_link="/contato/")),
    ("geral_404", "geral", "Página não encontrada (404)", dict(
        sobretitulo="Erro 404", titulo="Essa página não existe (ou mudou de lugar).", destaque="não existe",
        botao_texto="Ir para o início", botao_link="/", botao2_texto="Monte sua equipe",
        botao2_link="/monte-sua-equipe/")),
    ("sobre_topo", "sobre", "Topo", dict(
        sobretitulo="A empresa", titulo="Conectar soluções para desenvolver organizações.",
        destaque="desenvolver organizações",
        subtitulo="Confiança, credibilidade e organização a serviço da evolução dos nossos clientes.")),
    ("sobre_manifesto", "sobre", "Quem somos", dict(
        sobretitulo="Quem somos", titulo="Uma identidade construída sobre confiança, estratégia e evolução.",
        destaque="estratégia e evolução",
        texto="A Empreender Soluções é especializada em mão de obra e apoio administrativo. Montamos e gerimos "
              "equipes para que empresas e órgãos públicos possam concentrar energia no que é estratégico.\n\n"
              "Nossa identidade transmite os valores que guiam o trabalho: confiança, credibilidade, organização, "
              "sofisticação e desenvolvimento empresarial. Conectamos estratégias, organizamos processos e "
              "desenvolvemos soluções para a evolução dos negócios.\n\n"
              "O verde profundo da marca representa confiança e estabilidade. O champagne acrescenta cuidado e "
              "valor. E as formas interligadas do símbolo representam a conexão entre soluções e o movimento "
              "contínuo de desenvolvimento.")),
    ("sobre_simbolo", "sobre", "O que o símbolo representa", dict(
        sobretitulo="O símbolo", titulo="Diferentes elementos trabalhando juntos", destaque="trabalhando juntos",
        subtitulo="Faixas geométricas interligadas formam uma estrutura contínua e dinâmica, como uma solução completa.",
        itens="Estrutura e organização | Planejamento, estruturação e uma empresa que trabalha com direcionamento e "
              "visão estratégica.\n"
              "Integração e conexão | Conexão entre áreas, processos e soluções em busca de objetivos comuns.\n"
              "Movimento e desenvolvimento | Evolução e transformação: desenvolvimento empresarial e novas "
              "oportunidades.\n"
              "Equilíbrio e estabilidade | Segurança, consistência e confiança nas relações empresariais.")),
    ("servicos_topo", "servicos", "Topo", dict(
        sobretitulo="Serviços", titulo="Mão de obra e apoio administrativo sob medida", destaque="sob medida",
        subtitulo="Equipes selecionadas, treinadas e acompanhadas de perto, com gestão de contrato do início ao fim.")),
    ("servico_cta", "servicos", "Cartão lateral da página de cada serviço", dict(
        sobretitulo="Outros serviços", titulo="Precisa de {servico}?",
        texto="Conte o tamanho da equipe e a cidade. Retornamos com uma proposta sob medida.",
        botao_texto="Solicitar proposta")),
    ("proposta_etapas", "proposta", "Simulador · títulos das etapas e resumo", dict(
        sobretitulo="Resumo do pedido",
        subtitulo="Seus dados são usados apenas para responder a esta solicitação.",
        itens="Quais serviços você precisa?\nComo é a equipe?\nOnde será a operação?\nPara quem enviamos a proposta?")),
    ("proposta_sucesso", "proposta", "Simulador · mensagem após envio", dict(
        sobretitulo="Pedido recebido", titulo="Obrigado, {nome}! Sua solicitação está com a nossa equipe.",
        texto="Nossa equipe comercial vai analisar o pedido e entrar em contato pelo telefone ou e-mail informado.")),
    ("proposta_faq", "proposta", "Simulador · perguntas frequentes", dict(
        sobretitulo="Dúvidas", titulo="Antes de contratar", destaque="contratar")),
    ("proposta_topo", "proposta", "Topo", dict(
        sobretitulo="Monte sua equipe", titulo="Monte sua equipe em 4 etapas", destaque="4 etapas",
        subtitulo="Escolha os serviços, o tamanho da equipe e o local. Nossa equipe comercial retorna com uma "
                  "proposta sob medida.")),
    ("carreiras_topo", "carreiras", "Topo", dict(
        sobretitulo="Carreiras", titulo="Seu próximo passo começa aqui", destaque="começa aqui",
        subtitulo="Vagas abertas, banco de talentos e acompanhamento da candidatura pelo protocolo.")),
    ("carreiras_vagas", "carreiras", "Lista de vagas", dict(
        sobretitulo="Oportunidades", titulo="Vagas abertas", destaque="abertas",
        texto="Nenhuma vaga aberta no momento. Cadastre seu currículo no banco de talentos e avisaremos quando "
              "surgir uma oportunidade.", botao_texto="Acompanhar candidatura", botao_link="/carreiras/acompanhar/")),
    ("acompanhar_topo", "carreiras", "Acompanhar candidatura · topo", dict(
        sobretitulo="Carreiras", titulo="Acompanhe sua candidatura", destaque="candidatura",
        subtitulo="Informe o protocolo recebido ao se candidatar e o e-mail usado na inscrição.")),
    ("carreiras_form", "carreiras", "Formulário de currículo", dict(
        sobretitulo="Banco de talentos", titulo="Envie seu currículo", destaque="currículo",
        texto="Escolha uma vaga ou entre para o banco de talentos. Assim que você enviar, receberá um número de "
              "protocolo para acompanhar sua candidatura.",
        itens="Escolha a vaga ou o banco de talentos\nPreencha seus dados e anexe o currículo\n"
              "Guarde o protocolo e acompanhe pelo site")),
    ("contato_topo", "contato", "Topo", dict(
        sobretitulo="Contato", titulo="Vamos conversar", destaque="conversar",
        subtitulo="Escolha o canal mais adequado ou envie uma mensagem. Respondemos em horário comercial.")),
    ("contato_canais", "contato", "Canais e formulário", dict(
        titulo="Envie uma mensagem", botao_texto="Quero contratar", botao_link="/monte-sua-equipe/",
        botao2_texto="Quero trabalhar", botao2_link="/carreiras/",
        itens="Monte sua equipe em 4 etapas\nVagas e banco de talentos")),
    ("contato_faq", "contato", "Perguntas frequentes", dict(
        sobretitulo="Perguntas frequentes", titulo="Respostas rápidas", destaque="rápidas")),
    ("conteudos_topo", "conteudos", "Topo", dict(
        sobretitulo="Conteúdos", titulo="Gestão, carreiras e novidades", destaque="novidades",
        subtitulo="Artigos e comunicados para quem contrata e para quem quer trabalhar com a gente.")),
]

SERVICOS = [
    ("Terceirização de mão de obra", "equipe",
     "Equipes completas selecionadas, contratadas e geridas por nós.",
     "Cuidamos de todo o ciclo da mão de obra: recrutamento, seleção, contratação, treinamento, escalas, "
     "cobertura de ausências e gestão do contrato. Sua organização recebe a equipe pronta para trabalhar.",
     "Recrutamento e seleção\nAdmissão e documentação trabalhista\nTreinamento e integração\n"
     "Gestão de escalas e cobertura\nSupervisão e indicadores do contrato",
     "Auxiliar de serviços gerais\nCopeira\nMotorista\nAuxiliar de manutenção\nEncarregado"),
    ("Apoio administrativo", "pasta",
     "Profissionais para rotinas administrativas, documentação e atendimento interno.",
     "Estruturamos equipes de apoio para áreas administrativas, com profissionais preparados para rotinas de "
     "escritório, documentação, arquivo, protocolo e suporte às áreas da sua organização.",
     "Rotinas de escritório e protocolo\nOrganização de documentos e arquivo\nDigitação e cadastros\n"
     "Apoio a compras e almoxarifado",
     "Assistente administrativo\nAuxiliar de escritório\nDigitador\nArquivista\nAlmoxarife"),
    ("Recepção e atendimento", "recepcao",
     "A primeira impressão da sua organização, com cordialidade e organização.",
     "Recepcionistas e atendentes preparados para receber, orientar e registrar o público, com padrão de "
     "atendimento alinhado à identidade do cliente.",
     "Recepção de visitantes e público\nAtendimento telefônico\nAgendamentos e registros\nPadrão de atendimento",
     "Recepcionista\nTelefonista\nAtendente"),
    ("Limpeza e conservação", "limpeza",
     "Ambientes limpos, organizados e bem cuidados todos os dias.",
     "Planos de limpeza e conservação por ambiente, com equipe dimensionada, rotinas definidas e "
     "acompanhamento de qualidade.",
     "Plano de limpeza por ambiente\nConservação predial\nJardinagem\nControle de qualidade",
     "Auxiliar de limpeza\nJardineiro\nEncarregado de limpeza"),
    ("Portaria e controle de acesso", "escudo",
     "Controle de entrada e saída de pessoas e veículos com procedimentos claros.",
     "Profissionais de portaria e controle de acesso treinados em procedimentos, registros e comunicação, "
     "contribuindo para a rotina segura do ambiente.",
     "Controle de acesso de pessoas e veículos\nRegistros e relatórios\nProcedimentos operacionais",
     "Porteiro\nControlador de acesso"),
    ("Gestão de equipes e facilities", "grafico",
     "Supervisão, indicadores e gestão do contrato em um só lugar.",
     "Para operações maiores, assumimos a gestão das equipes terceirizadas com supervisão de campo, "
     "indicadores de desempenho e reuniões periódicas de acompanhamento.",
     "Supervisão de campo\nIndicadores de desempenho\nRelatórios periódicos\nPlano de melhoria contínua",
     "Supervisor\nGestor de contrato"),
]

SEGMENTOS = [
    ("Setor público", "governo", "Prefeituras, secretarias e órgãos, com atenção às exigências de cada contrato."),
    ("Indústria", "fabrica", "Apoio operacional e administrativo para plantas e escritórios industriais."),
    ("Comércio e varejo", "loja", "Equipes para lojas, centros de distribuição e áreas de atendimento."),
    ("Saúde", "saude", "Recepção, limpeza e apoio para clínicas, laboratórios e hospitais."),
    ("Educação", "escola", "Escolas e instituições de ensino com rotinas bem organizadas."),
    ("Empresas e condomínios", "casa", "Escritórios corporativos, condomínios e espaços compartilhados."),
]

PILARES = [
    ("Confiança", "Segurança nas relações e nos serviços prestados."),
    ("Credibilidade", "Profissionalismo e consistência."),
    ("Organização", "Estrutura e planejamento."),
    ("Sofisticação", "Cuidado e qualidade na apresentação."),
    ("Desenvolvimento", "Evolução e construção de oportunidades."),
    ("Integração", "Conexão entre diferentes soluções empresariais."),
]

ETAPAS = [
    ("Diagnóstico", "Entendemos a operação, o volume de trabalho, os horários e as exigências do seu contrato."),
    ("Estruturação", "Dimensionamos a equipe, definimos perfis, escalas e uma proposta sob medida."),
    ("Implantação", "Selecionamos, contratamos e treinamos os profissionais e iniciamos a operação."),
    ("Acompanhamento", "Supervisão, indicadores e reuniões periódicas para manter a qualidade e evoluir."),
]

PERGUNTAS = [
    ("Como funciona a terceirização de mão de obra?",
     "Nós recrutamos, contratamos, treinamos e gerimos os profissionais. Sua organização define o escopo e "
     "acompanha os resultados, sem precisar cuidar da administração de pessoal."),
    ("Vocês atendem órgãos públicos?",
     "Sim. Atendemos organizações públicas e privadas e adaptamos a documentação e os processos às exigências "
     "de cada contrato."),
    ("Em quanto tempo uma equipe pode começar?",
     "Depende do número de profissionais, dos perfis e da cidade. No primeiro contato, nossa equipe comercial "
     "informa um prazo realista para a sua demanda."),
    ("Como solicito uma proposta?",
     "Use o “Monte sua equipe”: escolha os serviços, a quantidade de profissionais e o local. Você recebe um "
     "protocolo e nossa equipe entra em contato."),
    ("Como me candidato a uma vaga?",
     "Acesse Carreiras, escolha uma vaga ou o banco de talentos e envie seu currículo. Você recebe um protocolo "
     "para acompanhar o andamento pelo site."),
]

PRIVACIDADE = """A Empreender Soluções respeita a sua privacidade e trata dados pessoais de acordo com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).

## Quais dados coletamos
Coletamos apenas os dados que você informa nos formulários do site: nome, e-mail, telefone, empresa, cidade, mensagens e, no caso de candidaturas, o currículo enviado.

## Para que usamos
Os dados são usados para responder ao seu contato, elaborar propostas comerciais e conduzir processos seletivos. Não vendemos nem compartilhamos seus dados para fins de marketing de terceiros.

## Cookies
Usamos cookies essenciais para o funcionamento do site. Cookies de medição de audiência só são ativados se você aceitar no aviso de cookies.

## Por quanto tempo guardamos
Mantemos os dados pelo tempo necessário para a finalidade informada ou para cumprir obrigações legais. Currículos do banco de talentos podem ser excluídos a qualquer momento, a seu pedido.

## Seus direitos
Você pode pedir acesso, correção ou exclusão dos seus dados pelo formulário de contato do site.

Este texto é um modelo inicial e deve ser revisado pelo responsável jurídico da empresa."""


class Command(BaseCommand):
    help = "Carrega o conteúdo inicial do site da Empreender Soluções."

    def add_arguments(self, parser):
        parser.add_argument("--sem-exemplos", action="store_true")
        parser.add_argument("--resetar", action="store_true")

    def handle(self, *args, **o):
        if o["resetar"]:
            for model in (m.Secao, m.Servico, m.Segmento, m.Pilar, m.Etapa, m.Pergunta, m.Aviso, m.Vaga,
                          m.Artigo, m.Pagina):
                model.objects.all().delete()
        m.Configuracao.carregar()

        for chave, pagina, nome, campos in SECOES:
            m.Secao.objects.get_or_create(chave=chave, defaults=dict(pagina=pagina, nome=nome, **campos))

        def carrega(model, linhas, fazer):
            if not model.objects.exists():
                for i, linha in enumerate(linhas):
                    fazer(i, *linha)

        carrega(m.Servico, SERVICOS, lambda i, t, ic, r, d, inc, perf: m.Servico.objects.create(
            titulo=t, icone=ic, resumo=r, descricao=d, inclui=inc, perfis=perf, ordem=i))
        carrega(m.Segmento, SEGMENTOS, lambda i, t, ic, tx: m.Segmento.objects.create(
            titulo=t, icone=ic, texto=tx, ordem=i))
        carrega(m.Pilar, PILARES, lambda i, t, tx: m.Pilar.objects.create(titulo=t, texto=tx, ordem=i))
        carrega(m.Etapa, ETAPAS, lambda i, t, tx: m.Etapa.objects.create(titulo=t, texto=tx, ordem=i))
        carrega(m.Pergunta, PERGUNTAS, lambda i, p, r: m.Pergunta.objects.create(pergunta=p, resposta=r, ordem=i))
        if not m.Pagina.objects.exists():
            m.Pagina.objects.create(titulo="Política de Privacidade", slug="privacidade", conteudo=PRIVACIDADE)

        if not o["sem_exemplos"]:
            self._exemplos()
        self.stdout.write(self.style.SUCCESS("Conteúdo da Empreender Soluções carregado."))

    def _exemplos(self):
        """Vagas, avisos e conteúdos de EXEMPLO — para ver como funciona. Edite ou apague no painel."""
        if m.Vaga.objects.exists():
            return
        hoje = timezone.localdate()
        s = {x.icone: x for x in m.Servico.objects.all()}
        v1 = m.Vaga.objects.create(
            titulo="Assistente administrativo", area=s.get("pasta"), cidade="Salvador", uf="BA", quantidade=3,
            resumo="Apoio às rotinas administrativas de um cliente do setor público: protocolo, arquivo e cadastros.",
            descricao="Organizar e arquivar documentos.\n\nRealizar cadastros e atualizar planilhas.\n\n"
                      "Atender o público interno e apoiar a coordenação da área.",
            requisitos="Ensino médio completo\nPacote Office básico\nBoa comunicação e organização",
            beneficios="Vale-transporte\nVale-alimentação\nPlano de carreira",
            prazo=hoje + timedelta(days=20), ordem=0)
        m.Vaga.objects.create(
            titulo="Recepcionista", area=s.get("recepcao"), cidade="Salvador", uf="BA", quantidade=2,
            resumo="Recepção de visitantes, atendimento telefônico e controle de agenda em escritório corporativo.",
            requisitos="Ensino médio completo\nExperiência com atendimento\nBoa apresentação",
            beneficios="Vale-transporte\nVale-alimentação", prazo=hoje + timedelta(days=15), ordem=1)
        m.Vaga.objects.create(
            titulo="Auxiliar de serviços gerais", area=s.get("equipe"), cidade="Feira de Santana", uf="BA",
            quantidade=8, resumo="Limpeza, organização e apoio operacional em unidade de cliente da indústria.",
            requisitos="Ensino fundamental completo\nDisponibilidade de horário",
            beneficios="Vale-transporte\nVale-alimentação\nCesta básica", prazo=hoje + timedelta(days=25), ordem=2)
        m.Vaga.objects.create(
            titulo="Banco de talentos · Portaria", area=s.get("escudo"), cidade="Salvador", uf="BA",
            regime="reserva", quantidade=10, destaque=False,
            resumo="Cadastro reserva para porteiros e controladores de acesso.", ordem=3)

        m.Aviso.objects.create(
            tipo="vagas", formato="modal", local="home", vaga=v1, frequencia="sessao",
            titulo="Estamos contratando!",
            texto="Vagas para assistente administrativo em Salvador. Envie seu currículo pelo site e acompanhe "
                  "sua candidatura pelo protocolo.", botao_texto="Ver vaga e me candidatar")
        m.Aviso.objects.create(
            tipo="edital", formato="faixa", local="todas", titulo="Processo seletivo aberto",
            texto="Vagas administrativas e operacionais na Bahia.", botao_texto="Ver vagas",
            botao_link="/carreiras/")
        m.Aviso.objects.create(
            tipo="novidade", formato="flutuante", local="home", frequencia="sessao",
            titulo="Novo: monte sua equipe online",
            texto="Escolha serviços e quantidade de profissionais e receba uma proposta.",
            botao_texto="Experimentar", botao_link="/monte-sua-equipe/")
        m.Aviso.objects.create(
            tipo="informativo", formato="secao", local="carreiras", titulo="Como acompanhar sua candidatura",
            texto="Ao enviar o currículo você recebe um protocolo. Use-o com seu e-mail em “Acompanhar "
                  "candidatura” para ver em que etapa está.", botao_texto="Acompanhar", botao_link="/carreiras/acompanhar/")

        if not m.Artigo.objects.exists():
            m.Artigo.objects.create(
                titulo="Terceirização de mão de obra: 5 pontos para avaliar antes de contratar", categoria="gestao",
                resumo="Escopo, dimensionamento, gestão de ausências, indicadores e conformidade: o que observar ao "
                       "escolher um parceiro.",
                conteudo="Terceirizar mão de obra pode liberar tempo e energia da sua equipe para o que é estratégico. "
                         "Para dar certo, alguns pontos merecem atenção desde o início.\n\n"
                         "## 1. Escopo bem definido\nDescreva as atividades, horários e locais. Quanto mais claro o "
                         "escopo, mais preciso o dimensionamento da equipe.\n\n"
                         "## 2. Dimensionamento\nO número de profissionais depende do volume de trabalho, da jornada "
                         "e da cobertura necessária em férias e ausências.\n\n"
                         "## 3. Gestão de ausências\nPergunte como o parceiro garante a continuidade do serviço "
                         "quando alguém falta.\n\n"
                         "## 4. Indicadores\nCombine como a qualidade será medida e com que frequência os "
                         "resultados serão apresentados.\n\n"
                         "## 5. Conformidade\nVerifique a regularidade trabalhista e fiscal do fornecedor e as "
                         "exigências específicas do seu setor.",
                data=timezone.now() - timedelta(days=2))
            m.Artigo.objects.create(
                titulo="Currículo para vagas administrativas: o que não pode faltar", categoria="carreiras",
                resumo="Dicas práticas para organizar o currículo e aumentar suas chances no processo seletivo.",
                conteudo="Um currículo claro facilita a triagem e mostra organização, uma qualidade essencial em "
                         "vagas administrativas.\n\n## Dados de contato atualizados\nTelefone com WhatsApp e um "
                         "e-mail que você consulta com frequência.\n\n## Objetivo direto\nUma linha dizendo a área "
                         "ou o cargo que você busca.\n\n## Experiências com resultados\nPara cada experiência, "
                         "cite atividades e, se possível, resultados.\n\n## Formação e cursos\nInclua cursos de "
                         "informática, atendimento e rotinas administrativas.\n\nDepois de enviar, guarde o "
                         "protocolo para acompanhar sua candidatura.",
                data=timezone.now() - timedelta(days=6))
            m.Artigo.objects.create(
                titulo="Empreender Soluções lança o “Monte sua equipe”", categoria="novidades",
                resumo="Agora é possível solicitar uma proposta de mão de obra e apoio administrativo em quatro etapas.",
                conteudo="Lançamos o “Monte sua equipe”, uma forma simples de solicitar propostas pelo site.\n\n"
                         "Em quatro etapas você escolhe os serviços, a quantidade de profissionais, o tipo de "
                         "contrato e o local da operação. Ao final, recebe um protocolo e nossa equipe comercial "
                         "entra em contato.",
                data=timezone.now() - timedelta(days=10))
