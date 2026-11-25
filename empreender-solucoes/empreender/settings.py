"""Configurações do projeto Empreender Soluções.

Valores sensíveis vêm de variáveis de ambiente ou do arquivo .env (veja .env.example).
"""
import os
from pathlib import Path

from django.templatetags.static import static
from django.urls import reverse_lazy

from ._env import carregar

BASE_DIR = Path(__file__).resolve().parent.parent
carregar(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [v.strip() for v in os.environ.get(name, default).split(",") if v.strip()]


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-inseguro-troque-em-producao-empreender-7c1d")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")
SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")  # ex.: https://www.empreendersolucoes.com

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "empreender.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "empreender.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", BASE_DIR / "db.sqlite3"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage" if DEBUG
        else "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = os.environ.get("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("DJANGO_EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.environ.get("DJANGO_DEFAULT_FROM_EMAIL", "site@localhost")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# ------------------------------------------------------------------ Painel (Unfold)
# Escala de cores gerada a partir do verde profundo #24483D (oklch 37% .046 172)
_VERDE = {
    "50": "oklch(97.5% .012 172)", "100": "oklch(94% .022 172)", "200": "oklch(88% .036 172)",
    "300": "oklch(78% .05 172)", "400": "oklch(64% .055 172)", "500": "oklch(52% .055 172)",
    "600": "oklch(44% .05 172)", "700": "oklch(37% .046 172)", "800": "oklch(31% .04 172)",
    "900": "oklch(26% .034 172)", "950": "oklch(19% .026 172)",
}
_BASE = {
    "50": "oklch(98.4% .005 88)", "100": "oklch(96.2% .009 88)", "200": "oklch(92% .012 88)",
    "300": "oklch(86% .012 100)", "400": "oklch(70% .012 130)", "500": "oklch(56% .013 150)",
    "600": "oklch(46% .014 158)", "700": "oklch(39% .014 158)", "800": "oklch(31% .013 158)",
    "900": "oklch(24% .012 158)", "950": "oklch(17% .01 158)",
}


def _url(name):
    return reverse_lazy(name)


UNFOLD = {
    "SITE_TITLE": "Empreender Soluções",
    "SITE_HEADER": "Empreender",
    "SITE_SUBHEADER": "Painel do site",
    "SITE_URL": "/",
    "SITE_SYMBOL": "dashboard",
    "SITE_ICON": lambda request: static("img/simbolo.png"),
    "SITE_LOGO": {"light": lambda r: static("img/logo.png"), "dark": lambda r: static("img/logo-negativa.png")},
    "SITE_FAVICONS": [{"rel": "icon", "sizes": "32x32", "type": "image/png",
                       "href": lambda request: static("img/favicon-32.png")}],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "DASHBOARD_CALLBACK": "core.dashboard.dashboard_callback",
    "STYLES": [lambda request: static("css/painel.css")],
    "LOGIN": {"image": lambda request: static("img/og.jpg")},
    "COLORS": {"base": _BASE, "primary": _VERDE},
    "COMMAND": {"search_models": True},
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {"title": "Visão geral", "items": [
                {"title": "Dashboard", "icon": "space_dashboard", "link": _url("admin:index")},
                {"title": "Ver o site", "icon": "open_in_new", "link": "/"},
            ]},
            {"title": "Comercial", "items": [
                {"title": "Propostas (Monte sua equipe)", "icon": "request_quote",
                 "link": _url("admin:core_proposta_changelist")},
                {"title": "Mensagens de contato", "icon": "mail", "link": _url("admin:core_mensagem_changelist")},
            ]},
            {"title": "Recrutamento", "items": [
                {"title": "Vagas", "icon": "work", "link": _url("admin:core_vaga_changelist")},
                {"title": "Candidaturas", "icon": "badge", "link": _url("admin:core_candidatura_changelist")},
            ]},
            {"title": "Comunicação", "items": [
                {"title": "Avisos (modal, faixa, seção…)", "icon": "campaign",
                 "link": _url("admin:core_aviso_changelist")},
                {"title": "Conteúdos / blog", "icon": "article", "link": _url("admin:core_artigo_changelist")},
            ]},
            {"title": "Conteúdo do site", "items": [
                {"title": "Textos das seções", "icon": "text_fields", "link": _url("admin:core_secao_changelist")},
                {"title": "Serviços", "icon": "handshake", "link": _url("admin:core_servico_changelist")},
                {"title": "Segmentos atendidos", "icon": "domain", "link": _url("admin:core_segmento_changelist")},
                {"title": "Pilares da marca", "icon": "diamond", "link": _url("admin:core_pilar_changelist")},
                {"title": "Etapas do processo", "icon": "timeline", "link": _url("admin:core_etapa_changelist")},
                {"title": "Números", "icon": "monitoring", "link": _url("admin:core_numero_changelist")},
                {"title": "Perguntas frequentes", "icon": "help", "link": _url("admin:core_pergunta_changelist")},
                {"title": "Depoimentos", "icon": "format_quote", "link": _url("admin:core_depoimento_changelist")},
                {"title": "Clientes (logos)", "icon": "workspace_premium",
                 "link": _url("admin:core_cliente_changelist")},
                {"title": "Páginas (privacidade…)", "icon": "description",
                 "link": _url("admin:core_pagina_changelist")},
            ]},
            {"title": "Configurações", "items": [
                {"title": "Dados da empresa", "icon": "tune", "link": _url("admin:core_configuracao_changelist")},
                {"title": "Usuários", "icon": "person", "link": _url("admin:auth_user_changelist")},
                {"title": "Grupos e permissões", "icon": "group", "link": _url("admin:auth_group_changelist")},
            ]},
        ],
    },
}
