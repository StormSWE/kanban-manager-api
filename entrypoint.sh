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

python << 'PY'
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
    except psycopg2.OperationalError:
        if time.time() > timeout:
            raise RuntimeError("Timed out waiting for Postgres")
        time.sleep(2)
PY

>&2 echo "[entrypoint] Resolved runtime DB information:"

python << 'PY'
import os
from urllib.parse import urlparse

dburl = os.environ.get('DATABASE_URL')

if dburl:
    parts = urlparse(dburl)
    dbname = parts.path[1:] if parts.path else ''
    user = parts.username
    print(f"DATABASE_URL host={parts.hostname} db={dbname} user={user}")
else:
    print("DATABASE_URL not set; using fallback sqlite")

hostenv = os.environ.get('POSTGRES_HOST')
if hostenv == 'host.docker.internal':
    print("WARNING: POSTGRES_HOST='host.docker.internal' — this bypasses the db container")
PY

>&2 echo "[entrypoint] Checking DB configuration consistency..."

python << 'PY'
import os
from urllib.parse import urlparse

dburl = os.environ.get('DATABASE_URL')
if dburl:
    parts = urlparse(dburl)
    url_user = parts.username
    url_db = parts.path[1:] if parts.path else ""
else:
    url_user = url_db = None

env_user = os.environ.get('POSTGRES_USER')
env_db = os.environ.get('POSTGRES_DB')

if url_user and env_user and url_user != env_user:
    print(f"WARNING: POSTGRES_USER={env_user} != DATABASE_URL user={url_user}")

if url_db and env_db and url_db != env_db:
    print(f"WARNING: POSTGRES_DB={env_db} != DATABASE_URL db={url_db}")
PY

>&2 echo "[entrypoint] Checking whether to apply migrations..."

run_migrations="${RUN_MIGRATIONS:-true}"

if [ "$run_migrations" = "true" ] || [ "$run_migrations" = "True" ]; then
    >&2 echo "[entrypoint] Applying migrations..."
    python manage.py migrate --noinput
else
    >&2 echo "[entrypoint] Skipping migrations (RUN_MIGRATIONS=${run_migrations})"
fi

>&2 echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput

>&2 echo "[entrypoint] Starting app with command: $*"
exec "$@"
