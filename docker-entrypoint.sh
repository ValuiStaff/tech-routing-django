#!/usr/bin/env bash
set -euo pipefail

# Default port
: "${PORT:=8000}"

echo "[entrypoint] Running database migrations..."
python manage.py migrate --noinput

# Optionally load a fixture file if provided and exists
if [[ -n "${FIXTURE_PATH:-}" ]]; then
  if [[ -f "$FIXTURE_PATH" ]]; then
    echo "[entrypoint] Loading fixture: $FIXTURE_PATH"
    python manage.py loaddata "$FIXTURE_PATH" || echo "[entrypoint] loaddata failed (continuing)."
  else
    echo "[entrypoint] FIXTURE_PATH set but file not found: $FIXTURE_PATH"
  fi
fi

# Optionally create an admin user if env vars provided
if [[ -n "${SUPERUSER_USERNAME:-}" && -n "${SUPERUSER_EMAIL:-}" && -n "${SUPERUSER_PASSWORD:-}" ]]; then
  echo "[entrypoint] Ensuring superuser exists: $SUPERUSER_USERNAME"
  python manage.py shell -c "from accounts.models import User;\n\
import os;\n\
username=os.environ.get('SUPERUSER_USERNAME');\n\
email=os.environ.get('SUPERUSER_EMAIL');\n\
password=os.environ.get('SUPERUSER_PASSWORD');\n\
qs=User.objects.filter(username=username);\n\
import sys;\n\
\nif not qs.exists():\n\
    User.objects.create_superuser(username=username, email=email, password=password, role='ADMIN');\n\
    print('Created superuser', username)\n\
else:\n\
    print('Superuser already exists', username)\n" || echo "[entrypoint] superuser creation failed (continuing)."
fi

# Start Gunicorn
echo "[entrypoint] Starting Gunicorn on :$PORT"
exec gunicorn tech_routing.wsgi:application \
  --bind 0.0.0.0:"${PORT}" \
  --workers ${GUNICORN_WORKERS:-3} \
  --threads ${GUNICORN_THREADS:-2} \
  --timeout ${GUNICORN_TIMEOUT:-120} \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --log-level info
