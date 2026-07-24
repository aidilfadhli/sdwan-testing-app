@echo off
title Mass Testing SD-WAN Telkom Indibiz
cd /d "%~dp0"

echo ==============================================
echo  Mass Testing SD-WAN Telkom Indibiz
echo ==============================================

if not exist ".venv\Scripts\python.exe" (
    echo [.venv] Mempersiapkan environment Python...
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
)

:: Jalankan Uvicorn server dengan SSL
start https://localhost:8000
.\.venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem

pause
