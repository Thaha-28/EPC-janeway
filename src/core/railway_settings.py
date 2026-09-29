"""Minimal production overlay for plain Janeway on Railway.

Loaded via JANEWAY_SETTINGS_MODULE=core.railway_settings.

Follows the upstream convention (see core/example_settings.py): define
ONLY overrides here. Janeway merges INSTALLED_APPS/MIDDLEWARE with the
global settings, so this module must NOT star-import them (that would
duplicate every app). MIDDLEWARE is therefore given in full.
"""
import os

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

# Console email unless SMTP is configured.
if not os.environ.get("JANEWAY_EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
