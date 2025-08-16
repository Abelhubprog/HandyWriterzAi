param(
  [switch]$All = $false,
  [switch]$Fast = $false,
  [string]$Req = "backend\requirements.txt",
  [string]$Args = ""
)

Write-Host "== HandyWriterzAI Windows test runner =="

# 1) Detect existing venvs or create one (version-agnostic)
$venvPath = ".venv"
$altVenvPath = "backend_env"

if (-not (Test-Path (Join-Path $venvPath "Scripts\Activate.ps1"))) {
  if (Test-Path (Join-Path $altVenvPath "Scripts\Activate.ps1")) {
    Write-Host "Using existing virtual environment at $altVenvPath"
    $venvPath = $altVenvPath
  } else {
    Write-Host "Creating .venv using available Python..."
    $created = $false
    try {
      & python -m venv $venvPath
      if ($LASTEXITCODE -eq 0) { $created = $true }
    } catch { }

    if (-not $created) {
      if (Get-Command py -ErrorAction SilentlyContinue) {
        try {
          & py -3 -m venv $venvPath
          if ($LASTEXITCODE -eq 0) { $created = $true }
        } catch { }
      }
    }

    if (-not $created) {
      Write-Error "Failed to create virtual environment ($venvPath). Ensure Python 3.x is installed and in PATH."
      exit 1
    }
  }
}

# 2) Activate venv
$venvActivate = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
  Write-Host "Activating venv..."
  . $venvActivate
  Write-Host "Using venv at: $venvPath"
  Write-Host "Python version:"
  python --version
} else {
  Write-Error "Failed to activate venv at $venvActivate (venv creation may have failed)"
  exit 1
}

# 3) Install dependencies
Write-Host "Installing deps from $Req..."
python -m pip install --upgrade pip | Out-Null
if ($Fast) {
  Write-Host "Using fast install (only-if-needed, prefer-binary)"
  python -m pip install -r $Req --upgrade-strategy only-if-needed --prefer-binary
} else {
  python -m pip install -r $Req
}

# 4) Set PYTHONPATH for mixed import styles
$env:PYTHONPATH = ".;backend;backend\src"
Write-Host "PYTHONPATH=$env:PYTHONPATH"

# 5) Control service-heavy tests via env
if ($All) {
  $env:RUN_REQUIRES_SERVICES = "1"
  Write-Host "Running ALL tests, including service-heavy (DB/Redis/API)"
  if ($env:DATABASE_URL) {
    Write-Host "Optional: running alembic upgrade head (DATABASE_URL detected)"
    pushd backend
    try {
      alembic upgrade head
    } catch {
      Write-Warning "Alembic migration failed: $_"
    } finally {
      popd
    }
  } else {
    Write-Host "Tip: Set DATABASE_URL for migrations; skipping alembic."
  }
} else {
  $env:RUN_REQUIRES_SERVICES = "0"
  Write-Host "Running unit tests only (service-heavy tests skipped). Use -All to include."
}

# 6) Run pytest
Write-Host "Running pytest..."
pytest -q $Args
