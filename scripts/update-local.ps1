# update-local.ps1
# Lokales Aequivalent zur Gitea Action: validiert und regeneriert alle
# generierten Dateien (health-profile.json und Markdown-Reports).
#
# Aufruf:
#   .\scripts\update-local.ps1
#   .\scripts\update-local.ps1 -Version 1.2.0

param(
    [string]$Version = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

function Write-Step($msg) {
    Write-Host ""
    Write-Host "-- $msg" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "   OK  $msg" -ForegroundColor Green
}

function Write-Fail($msg) {
    Write-Host "   ERR $msg" -ForegroundColor Red
}

# ── Version ermitteln ─────────────────────────────────────────────────────────

if (-not $Version) {
    try {
        $json = Get-Content "health-profile.json" -Raw | ConvertFrom-Json
        $Version = $json.version
        if (-not $Version -or $Version -eq "") { $Version = "unreleased" }
    } catch {
        $Version = "unreleased"
    }
}

Write-Host ""
Write-Host "PreNUDGE Health Profile -- lokales Update" -ForegroundColor White
Write-Host "Version: $Version"

# ── Validate ──────────────────────────────────────────────────────────────────

Write-Step "Referenzintegritaet pruefen (validate.py)"
python scripts/validate.py --strict
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Validierung fehlgeschlagen -- Abbruch."
    exit 1
}
Write-Ok "Keine Fehler gefunden."

# ── Consolidate ───────────────────────────────────────────────────────────────

Write-Step "JSON konsolidieren (consolidate.py)"
python scripts/consolidate.py --version $Version
if ($LASTEXITCODE -ne 0) {
    Write-Fail "consolidate.py fehlgeschlagen -- Abbruch."
    exit 1
}
Write-Ok "health-profile.json aktualisiert."

# ── Render Markdown ───────────────────────────────────────────────────────────

Write-Step "Markdown-Reports generieren (render_doc.py)"
python scripts/render_doc.py --version $Version --latest
if ($LASTEXITCODE -ne 0) {
    Write-Fail "render_doc.py fehlgeschlagen -- Abbruch."
    exit 1
}
Write-Ok "health-profile.de.md und .en.md aktualisiert."

# ── Render Browse-Ansicht ─────────────────────────────────────────────────────

Write-Step "Browse-Ansicht generieren (render_html.py)"
python scripts/render_html.py
if ($LASTEXITCODE -ne 0) {
    Write-Fail "render_html.py fehlgeschlagen -- Abbruch."
    exit 1
}
Write-Ok "render/browse.de.html und .en.html aktualisiert."

# ── Zusammenfassung ───────────────────────────────────────────────────────────

Write-Host ""
Write-Host "-- Fertig ------------------------------------------------------" -ForegroundColor Cyan
Write-Host "   Geaenderte Dateien:" -ForegroundColor White

$changed = git diff --name-only HEAD 2>$null
if ($changed) {
    $changed | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
} else {
    Write-Host "   (keine Aenderungen)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "   Naechster Schritt: git add + commit oder direkt pushen." -ForegroundColor Gray
Write-Host ""
