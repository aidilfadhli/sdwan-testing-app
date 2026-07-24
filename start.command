#!/bin/zsh
# Jalankan aplikasi Mass Testing SD-WAN (klik dua kali file ini di Finder)
cd "$(dirname "$0")"
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "IP-laptop-ini")

# Sertifikat HTTPS (perlu agar kamera HP bisa dipakai sebagai scanner).
# Dibuat ulang otomatis bila IP laptop berubah.
if [[ ! -f certs/cert.pem ]] || ! openssl x509 -in certs/cert.pem -noout -text | grep -q "IP Address:$IP"; then
  echo "Membuat sertifikat HTTPS untuk IP $IP …"
  mkdir -p certs
  openssl req -x509 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem \
    -days 1825 -nodes -subj "/CN=Mass Testing SDWAN" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:$IP" 2>/dev/null
fi

echo "=============================================="
echo " Mass Testing SD-WAN"
echo " Buka di laptop ini : https://localhost:8000"
echo " Dari HP operator   : https://$IP:8000"
echo " (atau scan QR di halaman utama aplikasi)"
echo " Peringatan sertifikat di browser: pilih Advanced/Lanjutkan."
echo " Tekan Ctrl+C untuk berhenti."
echo "=============================================="
open "https://localhost:8000" 2>/dev/null
exec .venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 \
  --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
