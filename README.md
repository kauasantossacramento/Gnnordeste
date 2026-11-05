# Grupo Nordeste — site em Django

Site institucional do **Grupo Nordeste**, refeito em Django a partir do conteúdo, da logo e das cores de
gnnordeste.com.br. Visual novo, com animações e painel administrativo completo.

## Rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py popular_site        # carrega textos, unidades, imagens e exemplos
python manage.py createsuperuser
python manage.py runserver
```

- Site: http://localhost:8000
- Painel: http://localhost:8000/painel/

`popular_site --sem-exemplos` não cria as vagas, avisos e notícias de exemplo.
`popular_site --resetar` apaga o conteúdo editável e recarrega o original.

Testes: `python manage.py test core`

## O que dá para fazer no painel (`/painel/`)

| Menu | Para quê |
|---|---|
| ⚙️ Configurações do site | Logo, telefone, WhatsApp (botão flutuante), e-mail, endereço, mapa, redes sociais |
| 📝 Textos das seções | Todos os títulos, textos, listas, imagens e botões de cada seção de cada página |
| 📢 Avisos | Avisos de contratação, edital, informativo, urgente ou evento, em 3 formatos: **cartão dentro de uma seção**, **modal** (janela ao abrir a página) ou **faixa** no topo. Tem período de exibição, frequência do modal, imagem, anexo PDF e vínculo com uma vaga |
| 💼 Vagas de emprego | Cargo, unidade, regime, nº de vagas, requisitos, edital, prazo. Cada vaga tem página e formulário próprios |
| 🪪 Candidaturas | Currículos recebidos, com status (nova → entrevista → aprovada) e observações internas |
| 📍 Unidades | Cidades em operação ou em implantação, com foto e página própria |
| 🛎️ Serviços / 📈 Números | Cartões de serviços e contadores animados |
| 🖼️ Banner / 📷 Galeria | Imagens do banner principal (trocam sozinhas) e galeria de fotos |
| 📰 Notícias | Publicações com capa |
| 📄 Documentos | Editais e Códigos de Ética (envie os PDFs e marque como ativos) |
| ✉️ Mensagens / 🛡️ Denúncias | Formulário de contato e canal de denúncias (anônimo, com protocolo e consulta pública da resposta) |

## Publicar (produção)

1. Copie `.env.example` para `.env` e preencha (`DJANGO_SECRET_KEY` longa, `DJANGO_DEBUG=false`, domínios).
2. `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
3. Rode com `gunicorn gnnordeste.wsgi` atrás do Nginx/Apache com HTTPS.
   Os arquivos estáticos já são servidos pelo WhiteNoise. Os uploads (`/media/`) são servidos pelo Django por
   padrão; com Nginx, sirva a pasta `media/` direto e use `DJANGO_SERVE_MEDIA=false`.
4. Para receber os formulários por e-mail, configure o SMTP no `.env` e o campo
   "e-mail que recebe formulários" no painel.

## Estrutura

```
gnnordeste/        configurações do projeto
core/              models, views, painel, formulários, comando popular_site, testes
core/seed/         imagens e PDFs extraídos do site original
templates/         HTML (base, páginas, partes reutilizáveis)
static/            CSS, JS, fontes (Poppins/Rubik locais), logo
```

Paleta: azul-marinho `#1D274E`, laranja `#F94C30` e o degradê da logo (`#E8343A` → `#F7A23A`).
