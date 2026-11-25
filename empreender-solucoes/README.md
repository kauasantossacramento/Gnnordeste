# Empreender Soluções · site em Django

Site institucional da **Empreender Soluções** (mão de obra e apoio administrativo), feito a partir do
**Manual da Marca 2026**: verde profundo `#24483D`, champagne `#C5A875`, off-white `#F1EDE3`,
grafite `#353D38`, Poppins (títulos) e Inter (textos). As logos usadas são as do manual, sem recomposição.

## Rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py popular_site        # textos, serviços, FAQ, política de privacidade + exemplos
python manage.py createsuperuser
python manage.py runserver
```

Site: http://localhost:8000 · Painel: http://localhost:8000/painel/ · Testes: `python manage.py test core`

`popular_site --sem-exemplos` não cria vagas, avisos e conteúdos de exemplo.
`popular_site --resetar` apaga o conteúdo editável e recarrega o padrão.

## Tudo editável pelo painel (`/painel/`)

| Menu | O que edita |
|---|---|
| Dados da empresa | Nome, slogan, contatos, WhatsApp (botão flutuante), endereço/mapa, redes, **logos, símbolo, favicon e imagem de compartilhamento** (vazio = arte do manual), Google Analytics, texto de cookies |
| Textos das seções | 31 blocos: título, trecho em destaque, subtítulo, texto, lista, imagem e **dois botões** de cada seção de cada página, inclusive rodapé, 404, etapas do simulador e mensagens de sucesso |
| Serviços | Nome, ícone, resumo, descrição, “o que inclui” e perfis profissionais (alimentam o simulador) |
| Segmentos, Pilares, Etapas, Números, FAQ, Depoimentos, Clientes | Blocos de conteúdo com ordem e “visível no site” |
| Avisos | Contratação, edital, informativo, urgente ou novidade em 4 formatos: **cartão em seção**, **modal**, **faixa no topo** ou **cartão flutuante**, com período, frequência, imagem, anexo e vínculo a uma vaga |
| Vagas / Candidaturas | Vagas com cidade, regime, modalidade, requisitos, benefícios, prazo e edital. Candidaturas com status, mensagem ao candidato (visível na consulta do protocolo) e notas internas |
| Propostas | Pedidos do “Monte sua equipe”, com funil comercial (nova → em contato → enviada → fechada) |
| Conteúdos / Páginas | Blog com categorias; páginas livres (ex.: Política de Privacidade) com link no rodapé |

Ficam fixos no código apenas os itens do menu de navegação e rótulos de formulário.

## Recursos

- **Monte sua equipe**: simulador em 4 etapas, com resumo ao vivo e protocolo `PR-…`
- **Explorador de serviços** com abas acessíveis por teclado, linha do tempo do processo que acompanha a rolagem e letreiro de segmentos
- **Carreiras**: filtros por cidade, área e busca, upload de currículo, protocolo `CV-…` e página “Acompanhar candidatura”
- **SEO**: `sitemap.xml`, `robots.txt`, canonical, Open Graph e schema.org (`Organization`, `JobPosting` para o Google Vagas, `FAQPage`, `Service`, `Article`)
- **LGPD**: aceite nos formulários, aviso de cookies (o Analytics só carrega se aceito) e política editável
- **Painel**: Unfold nas cores da marca, dashboard com indicadores, gráfico de 14 dias, funil e últimos pedidos
- Antispam (honeypot), máscara de telefone, `prefers-reduced-motion`, sem dependências de JavaScript

## Publicar

1. Copie `.env.example` para `.env` e preencha (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, domínios, `SITE_URL`).
2. `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
3. `gunicorn empreender.wsgi` atrás de Nginx/Apache com HTTPS. Os estáticos saem pelo WhiteNoise. `/media/`
   é servido pelo Django, a não ser que você defina `DJANGO_SERVE_MEDIA=false` e sirva a pasta pelo Nginx.
4. Para receber os formulários por e-mail, configure o SMTP no `.env` e o “e-mail que recebe os formulários” no painel.
