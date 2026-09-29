"""Production settings overlay for Railway deployment.

Loaded via JANEWAY_SETTINGS_MODULE=core.railway_settings.
Uppercase names here override core.janeway_global_settings
(see utils.load_janeway_settings).
"""
import os

from core.janeway_global_settings import *  # noqa: F401,F403

# Override INSTALLED_APPS to bypass the failing plugin loading at module level.
# The original janeway_global_settings does INSTALLED_APPS += plugin_installed_apps.load_plugin_apps(BASE_DIR)
# which fails during Docker build because the plugins directory may not be populated yet.
# We set a known-working INSTALLED_APPS list instead.
INSTALLED_APPS = [
    "modeltranslation",
    "apps.JanewayAdminConfig",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.postgres",
    "django.contrib.contenttypes",
    # Installed Apps for EPC
    "install",
    "core",
    "journal",
    "press",
    "repository",
    "security",
    "comms",
    "metrics",
    "events",
    "identifiers",
    "review",
    "reports",
    "production",
    "copyediting",
    "cron",
]

# Ensure BASE_DIR and sys.path are set correctly for Railway volume.
# Re-compute BASE_DIR here to guarantee correct path.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "plugins"))

SECRET_KEY = os.environ.get("JANEWAY_SECRET_KEY", "railway-build-placeholder-key")
DEBUG = False
ALLOWED_HOSTS = ["*"]

# Serve static files directly from gunicorn (no separate web server).
_mw = list(MIDDLEWARE)
_WHITE_NOISE = "whitenoise.middleware.WhiteNoiseMiddleware"
if _WHITE_NOISE not in _mw:
    if _mw and _mw[0].endswith("SecurityMiddleware"):
        _mw.insert(1, _WHITE_NOISE)
    else:
        _mw.insert(0, _WHITE_NOISE)
MIDDLEWARE = tuple(_mw)

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Console email unless SMTP is configured.
if not os.environ.get("JANEWAY_EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Media location (Railway volume mount).
MEDIA_ROOT = os.environ.get("JANEWAY_MEDIA_ROOT", MEDIA_ROOT)
