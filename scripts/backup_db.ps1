# Usage: .\scripts\backup_db.ps1 [label]      e.g. phase1, phase2, final
[CmdletBinding()]
param (
    [string]$Label = "manual"
)

$ErrorActionPreference = "Stop"
$Root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }

$EnvFiles = @(
    (Join-Path $Root "backend\.env"),
    (Join-Path $Root ".env")
)

$EnvPath = $null
foreach ($f in $EnvFiles) {
    if (Test-Path $f) {
        $EnvPath = $f
        break
    }
}

if (-not $EnvPath) {
    Write-Error "No .env file found in backend/ or root."
}

# Parse .env key=value lines
$DbEnv = @{}
Get-Content $EnvPath | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $parts = $line -split "=", 2
        $DbEnv[$parts[0].Trim()] = $parts[1].Trim()
    }
}

$DbName = if ($DbEnv.ContainsKey("DB_NAME")) { $DbEnv["DB_NAME"] } else { $env:DB_NAME }
$DbUser = if ($DbEnv.ContainsKey("DB_USER")) { $DbEnv["DB_USER"] } else { $env:DB_USER }
$DbPass = if ($DbEnv.ContainsKey("DB_PASSWORD")) { $DbEnv["DB_PASSWORD"] } else { $env:DB_PASSWORD }
$DbHost = if ($DbEnv.ContainsKey("DB_HOST")) { $DbEnv["DB_HOST"] } else { "localhost" }
$DbPort = if ($DbEnv.ContainsKey("DB_PORT")) { $DbEnv["DB_PORT"] } else { "5432" }

if (-not $DbName) { throw "DB_NAME missing" }
if (-not $DbUser) { throw "DB_USER missing" }

$BackupDir = Join-Path $Root "db_backup"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

$OutFile = Join-Path $BackupDir "hotel_db_${Label}.sql"

$env:PGPASSWORD = $DbPass
try {
    & pg_dump -h $DbHost -p $DbPort -U $DbUser --no-owner --no-privileges --clean --if-exists -f $OutFile $DbName
    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump failed with exit code $LASTEXITCODE"
    }
}
finally {
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}

$fileSize = (Get-Item $OutFile).Length
Write-Host "Backup written: $OutFile ($fileSize bytes)"
$createCount = (Select-String -Path $OutFile -Pattern "CREATE TABLE" -SimpleMatch).Count
Write-Host "CREATE TABLE statements: $createCount"
