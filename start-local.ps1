param(
  [switch]$FrontendOnly,
  [switch]$BackendOnly,
  [switch]$NoVenv
)

# Helper: activate local .venv if present (Windows)
function Use-LocalVenv {
  param(
    [string]$RepoRoot
  )
  $venvActivate = Join-Path $RepoRoot ".venv\Scripts\Activate.ps1"
  if (Test-Path $venvActivate) {
    Write-Host "🐍 Activating .venv from $venvActivate" -ForegroundColor Cyan
    . $venvActivate
    $true
  } else {
    $false
  }
}

if(-not $BackendOnly){
  Write-Host "▶️  Starting frontend (Next.js) in dev mode..." -ForegroundColor Green
  Start-Process -NoNewWindow -FilePath pnpm -ArgumentList 'dev' -WorkingDirectory "$PSScriptRoot\frontend"
}

if(-not $FrontendOnly){
  Push-Location "$PSScriptRoot\backend"

  if(-not $NoVenv){
    # Try to activate repo .venv if available
    Use-LocalVenv -RepoRoot $PSScriptRoot | Out-Null
  }

  # Ensure sensible dev defaults if not provided
  if(-not $env:API_HOST){ $env:API_HOST = "0.0.0.0" }
  if(-not $env:API_PORT){ $env:API_PORT = "8000" }
  if(-not $env:API_RELOAD){ $env:API_RELOAD = "true" }
  if(-not $env:REDIS_URL){ $env:REDIS_URL = "redis://localhost:6379" }
  if(-not $env:ALLOWED_ORIGINS){ $env:ALLOWED_ORIGINS = '["http://localhost:3000","http://localhost:3001"]' }

  # Prefer venv python if available, else fallback to system python
  $pythonExe = if (Test-Path "$PSScriptRoot\.venv\Scripts\python.exe") { "$PSScriptRoot\.venv\Scripts\python.exe" } else { "python" }
  Write-Host "🚀 Starting backend with: $pythonExe start_server.py" -ForegroundColor Green
  & $pythonExe start_server.py
  Pop-Location
}
