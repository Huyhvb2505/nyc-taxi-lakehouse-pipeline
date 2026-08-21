# run.ps1 — Windows PowerShell helper mirroring the Makefile.
# Windows has no `make`, so use this instead. Examples:
#   .\run.ps1 build
#   .\run.ps1 up
#   .\run.ps1 download -Year 2024 -Month 01
#   .\run.ps1 produce --limit 200000 --delay 0.2
#   .\run.ps1 down    /  .\run.ps1 clean
param(
    [Parameter(Position = 0)]
    [ValidateSet('build', 'up', 'down', 'restart', 'ps', 'logs', 'download', 'produce', 'clean', 'help')]
    [string]$Command = 'help',

    [string]$Year = '2024',
    [string]$Month = '01',

    # Extra args forwarded verbatim to `produce` (e.g. --limit 5000 --delay 0)
    [Parameter(ValueFromRemainingArguments = $true)]
    $Rest
)

switch ($Command) {
    'build'    { docker compose build }
    'up'       { docker compose up -d }
    'down'     { docker compose down }
    'restart'  { docker compose down; docker compose up -d }
    'ps'       { docker compose ps }
    'logs'     { docker compose logs -f }
    'download' { docker compose run --rm downloader $Year $Month }
    'produce'  { docker compose run --rm trip-producer @Rest }
    'clean'    { docker compose down -v }
    default {
        Write-Host "Usage: .\run.ps1 <command>"
        Write-Host ""
        Write-Host "  build      Build all custom images"
        Write-Host "  up         Start the cluster"
        Write-Host "  down       Stop the cluster (keeps volumes)"
        Write-Host "  restart    down + up"
        Write-Host "  ps         Show running services"
        Write-Host "  logs       Tail logs"
        Write-Host "  download   Download data:  .\run.ps1 download -Year 2024 -Month 01"
        Write-Host "  produce    Replay parquet to Kafka:  .\run.ps1 produce --limit 200000 --delay 0.2"
        Write-Host "  clean      Stop and DELETE all volumes"
    }
}
