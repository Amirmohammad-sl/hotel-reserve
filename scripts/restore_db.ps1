# Usage: .\scripts\restore_db.ps1 <file.sql> [target_db]
[CmdletBinding()]
param (
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$File,

    [Parameter(Position = 1)]
    [string]$TargetDb
)

$ErrorActionPreference = "Stop"
$Root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }

if (-not (Test-Path $File)) {
    # Try resolving relative to Root if not found directly
    $FileFromRoot = Join-Path $Root $File
    if (Test-Path $FileFromRoot) {
        $File = $FileFromRoot
    } else {
        throw "File not found: $File"
    }
}

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

$DbEnv = @{}
Get-Content $EnvPath | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $parts = $line -split "=", 2
        $DbEnv[$parts[0].Trim()] = $parts[1].Trim()
    }
}

$DbName = if ($env:DB_NAME_OVERRIDE) { $env:DB_NAME_OVERRIDE } elseif ($DbEnv.ContainsKey("DB_NAME")) { $DbEnv["DB_NAME"] } else { $env:DB_NAME }
$DbUser = if ($DbEnv.ContainsKey("DB_USER")) { $DbEnv["DB_USER"] } else { $env:DB_USER }
$DbPass = if ($DbEnv.ContainsKey("DB_PASSWORD")) { $DbEnv["DB_PASSWORD"] } else { $env:DB_PASSWORD }
$DbHost = if ($DbEnv.ContainsKey("DB_HOST")) { $DbEnv["DB_HOST"] } else { "localhost" }
$DbPort = if ($DbEnv.ContainsKey("DB_PORT")) { $DbEnv["DB_PORT"] } else { "5432" }

$ActualDb = if ($TargetDb) { $TargetDb } else { $DbName }
if (-not $ActualDb) { throw "DB_NAME / TargetDb missing" }
if (-not $DbUser) { throw "DB_USER missing" }

$PsqlCmd = "psql"
if (-not (Get-Command "psql" -ErrorAction SilentlyContinue)) {
    $candidates = @(
        "C:\Program Files\PostgreSQL\18\bin\psql.exe",
        "C:\Program Files\PostgreSQL\17\bin\psql.exe",
        "C:\Program Files\PostgreSQL\16\bin\psql.exe"
    )
    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            $PsqlCmd = $cand
            break
        }
    }
}

$env:PGPASSWORD = $DbPass
try {
    & $PsqlCmd -h $DbHost -p $DbPort -U $DbUser -d $ActualDb -f $File
    if ($LASTEXITCODE -ne 0) {
        throw "psql restore failed with exit code $LASTEXITCODE"
    }
}
finally {
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}
