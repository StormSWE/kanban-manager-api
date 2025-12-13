# Check DB connectivity from inside the web container
# Usage: ./scripts/check-db.ps1

$envFile = '.env'
if (-not (Test-Path $envFile)) {
    Write-Error "No .env file found. Create one from .env.new or ensure environment variables are set."
    exit 1
}

Write-Host "Testing DATABASE_URL from web container..."

docker compose run --rm web python - <<'PY'
import os
import psycopg2

try:
    dsn = os.environ.get('DATABASE_URL')
    if not dsn:
        print('DATABASE_URL not set in environment')
    else:
        print('DATABASE_URL:', dsn)
        conn = psycopg2.connect(dsn)
        print('Connected to DB:', conn.dsn)
        conn.close()
except Exception as e:
    print('Connection test failed:', e)
    raise
PY
