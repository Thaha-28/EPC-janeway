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
u, created = User.objects.get_or_create(username='$JANEWAY_ADMIN_USER', defaults={'email': '$JANEWAY_ADMIN_EMAIL'})
u.email = '$JANEWAY_ADMIN_EMAIL'
u.set_password('$JANEWAY_ADMIN_PASSWORD')
u.is_staff = True
u.is_superuser = True
u.is_active = True
u.save()
print('admin ready:', u.username)
" || echo "WARNING: admin setup failed (continuing)"
fi

echo "Starting gunicorn on 0.0.0.0:${PORT}..."
exec gunicorn core.wsgi:application --chdir src --bind "0.0.0.0:${PORT}" --workers 2 --timeout 120 --access-logfile - --error-logfile -
