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
from press import models as press_models
from journal import models as journal_models
from utils import install
domain = '$SITE_DOMAIN'
install.update_settings(management_command=False)
press, created = press_models.Press.objects.get_or_create(domain=domain, defaults={'name': 'EPC Press', 'main_contact': 'editors@epc-journal.org'})
print('press created:', domain) if created else print('press exists:', press.name)
journal = journal_models.Journal.objects.filter(code='epc').first()
if journal is None:
    install.journal(name='Environmental Processes and Chemistry', code='epc', base_url=domain, delete=False)
    install.update_issue_types(journal_models.Journal.objects.get(code='epc'), management_command=False)
    print('journal created: epc')
else:
    print('journal exists:', journal.code)
" || echo "WARNING: site bootstrap failed (continuing)"

echo "Starting gunicorn on 0.0.0.0:${PORT}..."
exec gunicorn core.wsgi:application --chdir src --bind "0.0.0.0:${PORT}" --workers 2 --timeout 120 --access-logfile - --error-logfile -
