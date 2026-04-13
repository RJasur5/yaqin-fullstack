Write-Host "--- Findix Project Cleaner ---" -ForegroundColor Yellow
# Kill any existing python/uvicorn processes before starting
taskkill /F /IM python.exe /T 2>$null
taskkill /F /IM uvicorn.exe /T 2>$null
Write-Host "Cleanup complete." -ForegroundColor Gray

Write-Host "--- Findix Project Launcher ---" -ForegroundColor Yellow

# Auto-detect IP and Update Flutter Config
Write-Host "--- Network Configuration ---" -ForegroundColor Yellow
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -eq 'Dhcp' -and $_.InterfaceAlias -notlike '*Loopback*' } | Select-Object -First 1).IPAddress
if (!$ip) {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike '*Loopback*' } | Select-Object -First 1).IPAddress
}

if ($ip) {
    Write-Host "Detected local IP: $ip" -ForegroundColor Cyan
    $configPath = Join-Path $PSScriptRoot "findix_app\lib\config\api_config.dart"
    if (Test-Path $configPath) {
        $content = Get-Content $configPath -Raw
        $newContent = $content -replace "static const String baseUrl = '.*';", "static const String baseUrl = 'http://$($ip):8005';"
        $newContent | Set-Content $configPath
        Write-Host "Updated api_config.dart with current IP." -ForegroundColor Green
    } else {
        Write-Warning "api_config.dart not found at $configPath"
    }
} else {
    Write-Warning "Could not detect local IP address."
}

# Backend
Write-Host "[1/2] Starting Findix Backend..." -ForegroundColor Green
$backendPath = Join-Path $PSScriptRoot "backend"
if (Test-Path $backendPath) {
    # Check for venv
    $venvPath = Join-Path $backendPath "venv"
    if (Test-Path $venvPath) {
        # Run backend in a new window
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload --host 0.0.0.0 --port 8005"
    } else {
        Write-Error "Virtual environment not found in $venvPath. Please create it first."
        exit 1
    }
} else {
    Write-Error "Backend directory not found in $backendPath."
    exit 1
}

# Frontend
Write-Host "[2/2] Starting Findix Frontend..." -ForegroundColor Cyan
$frontendPath = Join-Path $PSScriptRoot "findix_app"
if (Test-Path $frontendPath) {
    Set-Location $frontendPath
    flutter run -d chrome
} else {
    Write-Error "Frontend directory not found in $frontendPath."
    exit 1
}
