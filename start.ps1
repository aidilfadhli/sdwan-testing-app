Set-Location $PSScriptRoot

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " Mass Testing SD-WAN Telkom Indibiz" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "[.venv] Mempersiapkan environment Python..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}

$ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi","Ethernet" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress -First 1)
if (-not $ip) { $ip = "localhost" }

Write-Host ""
Write-Host " Buka di laptop ini : https://localhost:8000" -ForegroundColor Green
Write-Host " Dari HP operator   : https://${ip}:8000" -ForegroundColor Green
Write-Host " (atau scan QR di halaman utama aplikasi)" -ForegroundColor Gray
Write-Host ""
Write-Host " Tekan Ctrl+C untuk berhenti." -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Cyan

Start-Process "https://localhost:8000"
.\.venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000 --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
