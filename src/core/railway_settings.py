"""Minimal production overlay for plain Janeway on Railway.

Loaded via JANEWAY_SETTINGS_MODULE=core.railway_settings.

Follows the upstream convention (see core/example_settings.py): define
ONLY overrides here. Janeway merges INSTALLED_APPS/MIDDLEWARE with the
global settings, so this module must NOT star-import them (that would
duplicate every app). MIDDLEWARE is therefore given in full.
"""
import os

from core import plugin_installed_apps

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("JANEWAY_SECRET_KEY", "change-me-in-railway-vars")
DEBUG = False
ALLOWED_HOSTS = ["*"]

# Railway terminates TLS at its edge proxy and forwards plain HTTP with
# X-Forwarded-Proto. Without these, Django sees insecure requests from a
# secure origin and rejects every POST with "CSRF verification failed".
SITE_HOST = os.environ.get(
    "JANEWAY_SITE_DOMAIN", "epc-janeway-production.up.railway.app"
).removeprefix("https://").removeprefix("http://").split("/")[0]
CSRF_TRUSTED_ORIGINS = [f"https://{SITE_HOST}"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Full stock middleware (from core.janeway_global_settings) with
# WhiteNoise inserted right after SecurityMiddleware so gunicorn can
# serve static files with no separate web server.
MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "core.middleware.TimezoneMiddleware",
    "core.middleware.SiteSettingsMiddleware",
    "core.middleware.MaintenanceModeMiddleware",
    "cron.middleware.CronMiddleware",
    "core.middleware.CounterCookieMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "core.middleware.PressMiddleware",
    "core.middleware.GlobalRequestMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "journal.middleware.LanguageMiddleware",
    "hijack.middleware.HijackUserMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
)
MERGEABLE_SETTINGS = set()

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Stock TEMPLATES with one addition: src/templates/vendor/ holds the three
# foundationform templates, which modern pip drops when wheel-building the
# git-based django-foundation-form package (its setup.py has no package_data).
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (
            [
                os.path.join(BASE_DIR, "templates"),
                os.path.join(BASE_DIR, "templates", "common"),
                os.path.join(BASE_DIR, "templates", "admin"),
                os.path.join(BASE_DIR, "templates", "vendor"),
            ]
            + plugin_installed_apps.load_plugin_templates(BASE_DIR)
            + plugin_installed_apps.load_homepage_element_templates(BASE_DIR)
        ),
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.journal",
                "core.context_processors.journal_settings",
                "core.context_processors.press",
                "core.context_processors.active",
                "core.context_processors.navigation",
                "core.context_processors.version",
                "django_settings_export.settings_export",
                "django.template.context_processors.i18n",
            ],
            "loaders": [
                "utils.template_override_middleware.Loader",
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "builtins": [
                "core.templatetags.fqdn",
                "core.templatetags.alt_text",
                "security.templatetags.securitytags",
                "django.templatetags.i18n",
            ],
        },
    },
]

# Console email unless SMTP is configured.
if not os.environ.get("JANEWAY_EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
