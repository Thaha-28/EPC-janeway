#!/bin/bash
set -e

export JANEWAY_SETTINGS_MODULE="${JANEWAY_SETTINGS_MODULE:-core.railway_settings}"
export PORT="${PORT:-8000}"

# Wait for Postgres (DATABASE_URL or separate vars).
if [ -n "$DATABASE_URL" ]; then
  DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^:/]*\).*|\1|p')
  DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
  export DB_VENDOR=postgres
  export DB_HOST DB_PORT
  export DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')
  export DB_USER=$(echo "$DATABASE_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
  export DB_PASSWORD=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
fi

if [ -n "$DB_HOST" ]; then
  echo "Waiting for database $DB_HOST:${DB_PORT:-5432}..."
  for i in $(seq 1 60); do
    if python -c "import socket; socket.create_connection(('$DB_HOST', int('${DB_PORT:-5432}')), timeout=5).close()" 2>/dev/null; then
      echo "Database reachable."
      break
    fi
    echo "Database not ready yet ($i/60)..."
    sleep 2
  done
fi

echo "Running migrations..."
python src/manage.py migrate --noinput

echo "Building theme assets (OLH/material/clean SCSS+JS)..."
python src/manage.py build_assets || echo "WARNING: build_assets failed (continuing)"

# EPC modern theme layer. The OLH theme loads press_override.css on press
# pages and default_override.css on journal pages; src/static is gitignored
# upstream so both are generated here from the committed deploy source.
mkdir -p src/static/OLH/css
cp deploy/epc-modern.css src/static/OLH/css/press_override.css
cp deploy/epc-modern.css src/static/OLH/css/default_override.css
echo "Theme overrides installed."

echo "Collecting static files..."
python src/manage.py collectstatic --noinput

# Admin account from env (idempotent).
if [ -n "$JANEWAY_ADMIN_USER" ] && [ -n "$JANEWAY_ADMIN_EMAIL" ] && [ -n "$JANEWAY_ADMIN_PASSWORD" ]; then
  echo "Ensuring admin account..."
  JANEWAY_ADMIN_USER="$JANEWAY_ADMIN_USER" JANEWAY_ADMIN_EMAIL="$JANEWAY_ADMIN_EMAIL" JANEWAY_ADMIN_PASSWORD="$JANEWAY_ADMIN_PASSWORD" python src/manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(email='$JANEWAY_ADMIN_EMAIL', defaults={'username': '$JANEWAY_ADMIN_USER'})
u.username = '$JANEWAY_ADMIN_USER'
u.set_password('$JANEWAY_ADMIN_PASSWORD')
u.is_staff = True
u.is_superuser = True
u.is_active = True
u.save()
print('admin ready:', u.username)
" || echo "WARNING: admin setup failed (continuing)"
fi

# Bootstrap press + journal with stock Janeway install helpers (idempotent).
# Without a press matching this host, Janeway redirects / to DEFAULT_HOST.
SITE_DOMAIN="${JANEWAY_SITE_DOMAIN:-${RAILWAY_PUBLIC_DOMAIN:-epc-janeway-production.up.railway.app}}"
SITE_DOMAIN="${SITE_DOMAIN#https://}"
SITE_DOMAIN="${SITE_DOMAIN#http://}"
echo "Ensuring press/journal for ${SITE_DOMAIN}..."
SITE_DOMAIN="$SITE_DOMAIN" python src/manage.py shell -c "
from django.core.management import call_command
from press import models as press_models
from journal import models as journal_models
from core import models as core_models
from utils import install
domain = '$SITE_DOMAIN'
install.update_settings(management_command=False)
# Role fixtures (utils/install/roles.json) are required for registration
# (add_account_role) and many staff flows. get_or_create by slug keeps this
# idempotent (plain loaddata would duplicate rows on every boot).
import json as _json, os as _os
from django.conf import settings as _settings
with open(_os.path.join(_settings.BASE_DIR, 'utils/install/roles.json')) as _f:
    _roles = _json.load(_f)
for _r in _roles:
    core_models.Role.objects.get_or_create(slug=_r['fields']['slug'], defaults={'name': _r['fields']['name']})
print('roles exist:', core_models.Role.objects.count())
press, created = press_models.Press.objects.get_or_create(domain=domain, defaults={'name': 'EPC Press', 'main_contact': 'editors@epc-journal.org'})
print('press created:', domain) if created else print('press exists:', press.name)
journal = journal_models.Journal.objects.filter(code='epc').first()
if journal is None:
    install.journal(name='Environmental Processes and Chemistry', code='epc', base_url='', delete=False)
    journal = journal_models.Journal.objects.get(code='epc')
    install.update_issue_types(journal, management_command=False)
    print('journal created: epc')
else:
    print('journal exists:', journal.code)
# Path-mode serving: the press owns the domain, journals live under /<code>/,
# so the journal itself must have a blank domain (else it matches by domain
# and /epc/ is not a valid in-journal path).
if journal.domain:
    journal.domain = None
    journal.save()
    print('journal domain cleared for path mode')
if journal.name != 'Environmental Processes and Chemistry':
    journal.name = 'Environmental Processes and Chemistry'
    print('journal name set')
# No real ISSNs yet: blank them so the footer does not show placeholders.
if journal.issn:
    journal.issn = ''
    print('journal issn cleared')
if journal.print_issn:
    journal.print_issn = ''
    print('print issn cleared')
from utils import setting_handler
setting_handler.save_setting('general', 'publisher_name', journal, 'Environmental Processes and Chemistry')
# Press footer middle column content.
if not press.footer_description:
    press.footer_description = 'Diamond open access publishing in environmental chemistry and process science. All content is published under a Creative Commons Attribution (CC BY) licence.'
    press.save()
    print('press footer description set')
# EPC branding: press thumbnail (header/footer logo) + journal header/footer
# images, from the committed deploy/epc-logo.svg.
import shutil as _shutil
from django.core.files.base import ContentFile as _ContentFile
_press_dir = _os.path.join(_settings.BASE_DIR, 'files', 'press')
_os.makedirs(_press_dir, exist_ok=True)
_press_logo = _os.path.join(_press_dir, 'epc-logo.svg')
if not _os.path.exists(_press_logo):
    _shutil.copy('deploy/epc-logo.svg', _press_logo)
    print('press logo file installed')
with open('deploy/epc-logo.svg', 'rb') as _lf:
    _svg = _lf.read()
_thumb, _tc = core_models.File.objects.get_or_create(uuid_filename='epc-logo.svg', defaults={'mime_type': 'image/svg+xml', 'original_filename': 'epc-logo.svg', 'label': 'EPC logo'})
if press.thumbnail_image_id != _thumb.pk:
    press.thumbnail_image = _thumb
    press.save()
    print('press thumbnail set')
if not journal.header_image:
    journal.header_image.save('epc-logo.svg', _ContentFile(_svg), save=True)
    print('journal header image set')
if not journal.press_image_override:
    journal.press_image_override.save('epc-logo.svg', _ContentFile(_svg), save=True)
    print('journal footer image set')
" || echo "WARNING: site bootstrap failed (continuing)"

# Seed EPC demo content (idempotent, no-op if journal missing).
if [ -f seed_epc.py ]; then
  echo "Seeding EPC content..."
  python src/manage.py shell < seed_epc.py || echo "WARNING: seed failed (continuing)"
fi

echo "Starting gunicorn on 0.0.0.0:${PORT}..."
exec gunicorn core.wsgi:application --chdir src --bind "0.0.0.0:${PORT}" --workers 2 --timeout 120 --access-logfile - --error-logfile -
