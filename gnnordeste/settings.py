"""Configurações do projeto Grupo Nordeste.

Valores sensíveis vêm de variáveis de ambiente (veja .env.example).
"""
import os
from pathlib import Path

from ._env import carregar

BASE_DIR = Path(__file__).resolve().parent.parent
carregar(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [v.strip() for v in os.environ.get(name, default).split(",") if v.strip()]


SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-inseguro-troque-em-producao-9f3c2b7a1e",
)
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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

ROOT_URLCONF = "gnnordeste.urls"

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

WSGI_APPLICATION = "gnnordeste.wsgi.application"

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
TIME_ZONE = "America/Bahia"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# E-mail: por padrão as mensagens só ficam no painel; configure SMTP para receber por e-mail.
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("DJANGO_EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.environ.get("DJANGO_DEFAULT_FROM_EMAIL", "site@gnnordeste.com.br")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ---------------------------------------------------------------- Painel (Jazzmin)
JAZZMIN_SETTINGS = {
    "site_title": "Grupo Nordeste",
    "site_header": "Grupo Nordeste",
    "site_brand": "Painel Nordeste",
    "site_logo": "img/simbolo.png",
    "login_logo": "img/logo.png",
    "site_icon": "img/favicon.png",
    "welcome_sign": "Painel administrativo do site",
    "copyright": "Grupo Nordeste",
    "search_model": ["core.Vaga", "core.Unidade"],
    "topmenu_links": [
        {"name": "Ver site", "url": "/", "new_window": True},
    ],
    "show_ui_builder": False,
    "order_with_respect_to": [
        "core.ConfiguracaoSite",
        "core.Secao",
        "core.Aviso",
        "core.Vaga",
        "core.Candidatura",
        "core.Unidade",
        "core.Servico",
        "core.Numero",
        "core.SlideHero",
        "core.ImagemGaleria",
        "core.Noticia",
        "core.Documento",
        "core.MensagemContato",
        "core.Denuncia",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.ConfiguracaoSite": "fas fa-sliders-h",
        "core.Secao": "fas fa-align-left",
        "core.Aviso": "fas fa-bullhorn",
        "core.Vaga": "fas fa-briefcase",
        "core.Candidatura": "fas fa-id-badge",
        "core.Unidade": "fas fa-map-marker-alt",
        "core.Servico": "fas fa-concierge-bell",
        "core.Numero": "fas fa-chart-line",
        "core.SlideHero": "fas fa-images",
        "core.ImagemGaleria": "fas fa-photo-video",
        "core.Noticia": "fas fa-newspaper",
        "core.Documento": "fas fa-file-pdf",
        "core.MensagemContato": "fas fa-envelope",
        "core.Denuncia": "fas fa-shield-alt",
    },
    "changeform_format": "horizontal_tabs",
}
JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-warning",
    "brand_colour": "navbar-dark",
    "accent": "accent-orange",
    "button_classes": {"primary": "btn-warning", "success": "btn-success"},
}
