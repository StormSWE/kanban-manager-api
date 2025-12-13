# Dev helper to quickly reset and run the Docker environment.
# WARNING: This will remove volumes if -ForceReset is used, deleting DB data.
param(
    [switch] $ForceReset = $false
)

# Copy template .env.new -> .env if .env doesn't exist or always if user agrees
if (-not (Test-Path .env)) {
    Copy-Item .env.new .env
    Write-Host "Copied .env.new -> .env"
}

if ($ForceReset) {
    Write-Host "Stopping containers and removing volumes..."
    docker compose down -v
}

Write-Host "Building and starting containers..."
docker compose up --build
