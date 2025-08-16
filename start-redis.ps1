param(
  [int]$Port = 6379
)

Write-Host "🔧 Starting Redis in Docker on port $Port..." -ForegroundColor Green

# Check Docker
$dockerOk = $false
try {
  docker ps | Out-Null
  $dockerOk = $true
} catch {
  $dockerOk = $false
}

if(-not $dockerOk){
  Write-Host "❌ Docker is not running or not installed." -ForegroundColor Red
  exit 1
}

$name = "handywriterz-redis"
$exists = docker ps -a --format '{{.Names}}' | Select-String -SimpleMatch $name
if(-not $exists){
  docker run -d --name $name -p ${Port}:6379 redis:7-alpine redis-server --appendonly yes | Out-Null
  Write-Host "✅ Redis container started as '$name'" -ForegroundColor Green
} else {
  $running = docker ps --format '{{.Names}}' | Select-String -SimpleMatch $name
  if(-not $running){
    docker start $name | Out-Null
    Write-Host "▶️  Redis container '$name' started" -ForegroundColor Green
  } else {
    Write-Host "✅ Redis container '$name' already running" -ForegroundColor Yellow
  }
}

Write-Host "🔍 Testing Redis connection..." -ForegroundColor Cyan
try {
  docker exec $name redis-cli ping | Out-Null
  Write-Host "✅ Redis is responding" -ForegroundColor Green
} catch {
  Write-Host "⚠️  Could not ping Redis inside container. Ensure port $Port is open." -ForegroundColor Yellow
}

