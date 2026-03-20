#!/bin/sh
set -e

mkdir -p /app/staticfiles /app/media "$(dirname "${SQLITE_PATH:-/app/db.sqlite3}")"

if [ -n "${DB_HOST:-}" ]; then
    echo "==> Waiting for PostgreSQL..."
    until python -c "
import os, sys
if os.environ.get('DB_HOST'):
    import psycopg2
    try:
        psycopg2.connect(
            dbname=os.environ.get('DB_NAME','solar_db'),
            user=os.environ.get('DB_USER','solar_user'),
            password=os.environ.get('DB_PASSWORD',''),
            host=os.environ.get('DB_HOST','db'),
            port=os.environ.get('DB_PORT','5432'),
        )
    except psycopg2.OperationalError:
        sys.exit(1)
" 2>/dev/null; do
        echo "   Database not ready, retrying in 2s..."
        sleep 2
    done
else
    echo "==> Using SQLite at ${SQLITE_PATH:-/app/db.sqlite3}"
fi

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-4}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
