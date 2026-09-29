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
