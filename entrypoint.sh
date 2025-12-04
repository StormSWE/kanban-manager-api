#!/bin/sh
set -o errexit
set -o pipefail
set -o nounset

postgres_host="${POSTGRES_HOST:-db}"
postgres_port="${POSTGRES_PORT:-5432}"
postgres_db="${POSTGRES_DB:-kanban}" 
postgres_user="${POSTGRES_USER:-kanban}"
postgres_password="${POSTGRES_PASSWORD:-kanban}" 

>&2 echo "[entrypoint] Waiting for Postgres ${postgres_host}:${postgres_port}..."
python <<'PY'
import os
import time
import psycopg2

host = os.environ.get('POSTGRES_HOST', 'db')
port = int(os.environ.get('POSTGRES_PORT', '5432'))
user = os.environ.get('POSTGRES_USER', 'kanban')
password = os.environ.get('POSTGRES_PASSWORD', 'kanban')
database = os.environ.get('POSTGRES_DB', 'kanban')

timeout = time.time() + 60
while True:
    try:
        psycopg2.connect(host=host, port=port, user=user, password=password, dbname=database).close()
        break
    except psycopg2.OperationalError as exc:  # pragma: no cover
        if time.time() > timeout:
            raise RuntimeError("Timed out waiting for Postgres") from exc
        time.sleep(2)
PY

>&2 echo "[entrypoint] Applying migrations"
python manage.py migrate --noinput

>&2 echo "[entrypoint] Collecting static files"
python manage.py collectstatic --noinput

>&2 echo "[entrypoint] Starting app with command: $*"
exec "$@"
