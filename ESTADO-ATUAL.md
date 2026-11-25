# Estado atual do repositório

_Atualizado em 25/11/2026._

Este repositório tem **dois sites Django independentes**, cada um com banco, painel e dependências próprios.

| Projeto | Pasta | Painel | Situação |
|---|---|---|---|
| **Grupo Nordeste** (reconstrução de gnnordeste.com.br) | raiz (`gnnordeste/`, `core/`, `templates/`, `static/`) | Jazzmin em `/painel/` | Concluído · 8 testes passando |
| **Empreender Soluções** (novo, a partir do Manual da Marca 2026) | `empreender-solucoes/` | Unfold em `/painel/` | Concluído · 11 testes passando |

Para rodar cada um: `pip install -r requirements.txt`, `python manage.py migrate`,
`python manage.py popular_site` e `python manage.py runserver`, de dentro da pasta do projeto.
Detalhes no README de cada um.

---

## 1. Grupo Nordeste (raiz)

**O que foi feito**
- Conteúdo, logo, cores (`#1D274E`, `#F94C30`, degradê da logo) e imagens extraídos do site original
- Páginas: início, quem somos, unidades (19, com página própria), trabalhe conosco (vagas + currículo), notícias, contato e canal de denúncias com protocolo
- Avisos em 3 formatos (seção, modal e faixa) e textos das seções editáveis no painel

**Pendências**
- O site original está **comprometido**: as notícias são spam de cassino e há um link oculto para `casino50.com`. Nada disso foi migrado.
- Enviar os PDFs dos Códigos de Ética no painel (Documentos) e ativá-los
- Preencher WhatsApp e redes sociais no painel
- Apagar as vagas, avisos e notícias de exemplo
- Trocar a senha do admin

## 2. Empreender Soluções (`empreender-solucoes/`)

**Estrutura**
```
empreender-solucoes/
├── empreender/          settings (Unfold com a paleta da marca), urls, sitemap, robots
├── core/
│   ├── models.py        Configuracao, Secao (31 blocos), Servico, Segmento, Pilar, Etapa, Numero,
│   │                    Pergunta, Depoimento, Cliente, Pagina, Artigo, Vaga, Candidatura,
│   │                    Proposta, Mensagem, Aviso
│   ├── admin.py         painel com selos de status, filtros e ações em massa
│   ├── dashboard.py     indicadores do painel inicial
│   ├── views.py         páginas e formulários (proposta, candidatura, contato, acompanhar)
│   ├── templatetags/    destaque de título, parágrafos, ícones, schema.org (JSON-LD)
│   ├── management/commands/popular_site.py   conteúdo inicial e exemplos
│   └── tests.py         11 testes (páginas, edição pelo painel, formulários, SEO, painel)
├── templates/           base, páginas em core/, partes reutilizáveis em partials/, dashboard em admin/
└── static/              css/site.css, css/painel.css, js/site.js, fontes locais, logos do manual
```

**Páginas:** início · a empresa · serviços (+ página de cada serviço) · monte sua equipe ·
carreiras (+ vaga, acompanhar candidatura) · conteúdos (+ artigo) · contato · páginas livres · 404

**Editável pelo painel:** todos os textos (31 blocos de seção com 2 botões cada), logos, símbolo,
favicon, imagem de compartilhamento, serviços, segmentos, pilares, etapas, FAQ, depoimentos, clientes,
vagas, avisos, conteúdos e páginas. Um teste automatizado confirma que alterações feitas no painel
(texto, seção oculta, logo nova) aparecem no site.

**Decisões**
- A logo não foi redesenhada em SVG: o manual proíbe recompor os elementos. As faixas animadas do site são decorativas, inspiradas na capa do manual.
- Champagne não é usado como cor de texto sobre fundo claro (contraste insuficiente, conforme o manual). Nesse caso o destaque vira verde com sublinhado champagne.
- Nenhum telefone, endereço, número ou depoimento foi inventado. Esses campos começam vazios, e as seções correspondentes ficam ocultas até serem preenchidas.

**Pendências**
- Preencher telefone, WhatsApp, e-mail, endereço, CNPJ e redes em “Dados da empresa”
- Revisar os textos institucionais (escritos a partir do manual) e a Política de Privacidade (modelo, precisa de revisão jurídica)
- Apagar as vagas, avisos e conteúdos de exemplo
- Registrar o domínio e definir `SITE_URL` / `DJANGO_ALLOWED_HOSTS`
- Trocar a senha do admin

**Domínio (consulta RDAP/whois em 25/11/2026)**

| Domínio | Situação |
|---|---|
| empreendersolucoes.com.br | **Registrado** desde 23/01/2026 (titular pessoa física). Se for da empresa, use este. |
| empreendersolucoes.com | Livre · **recomendado** se o .com.br não for de vocês |
| empreenderservicos.com.br | Livre na primeira consulta |
| empreendersol.com.br, empreendergestao.com.br, somosempreender.com.br | Livres |
| empreendersolucoes.net.br, empreendersolucoes.srv.br, empreender.adm.br, empreender.srv.br | Livres |
| empreender.com.br, grupoempreender.com.br, empreenderbr.com.br | Registrados |

Disponibilidade muda a qualquer momento; confirme no Registro.br na hora de registrar.
