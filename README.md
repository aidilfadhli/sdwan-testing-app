# Mass Testing SD-WAN — Form Digital Berita Acara Uji Fungsi (Multi-Vendor)

Aplikasi web lokal untuk uji fungsi massal (*Uji Fungsi*) perangkat **SD-WAN Edge Multi-Vendor** (**Fortinet**, **Cisco**, dan **VMware VeloCloud**) di gudang.

Menggantikan pengisian manual dokumen *Berita Acara Uji Fungsi*: operator scan S/N (via scanner hardware atau kamera HP), memilih/auto-detect vendor, mengisi checklist uji fungsi interaktif, mengunggah foto bukti ber-watermark otomatis, dan aplikasi secara instan:

- Menyimpan seluruh hasil pengujian dan riwayat versi ke database (**SQLite**),
- Menyusun folder bukti foto per perangkat (`data/evidence/<SN>_r<id>/`),
- **Menghasilkan Berita Acara .docx** resmi sesuai format vendor (`ba_template_fortinet.docx`, `ba_template_cisco.docx`, `ba_template_velocloud.docx`) dengan layout tanda tangan 2x2,
- Menyediakan **Export Excel Multi-Sheet** (Ringkasan + Tab Per Vendor),
- Menampilkan **Dashboard Analytics Visual** (Donut chart PASS/FAIL, Tren Harian 14 Hari, dan Ranking Item Gagal).

---

## 🚀 Fitur Utama

### 1. Multi-Vendor Engine & Auto-Detection (`checklist.py`)
- **Fortinet SD-WAN Edge** (Prefix: `FGT`, `FG`): 6 item uji baseline, 6 seksi foto.
- **Cisco SD-WAN Edge** (Prefix: `FGL`, `FOC`): 6 item uji baseline, 6 seksi foto.
- **VMware VeloCloud SD-WAN Edge** (Prefix: `VC`): 7 item uji baseline (termasuk SFP & LAN GE), 6 seksi foto.
- Terintegrasi auto-detect vendor saat scan S/N.

### 2. Barcode Scanning & Smart Duplicate Handling
- **Dua Metode Scan**: Scanner hardware IWare (keyboard emulation) atau **Kamera HP** berbasis browser (`HTML5-QRCode`) via HTTPS.
- **Smart Duplicate Prompt (`duplicate_prompt.html`)**: Jika S/N sudah pernah diuji, operator diberi pilihan:
  - *Uji Ulang (Re-Test)*: Membuat rekam uji baru dengan riwayat versi bertingkat (`version = N`).
  - *Edit Laporan Terakhir*: Memperbaiki data pengujian sebelumnya.
  - *Lihat Riwayat Audit*: Meninjau pohon riwayat versi pengujian perangkat.

### 3. Pengeditan Laporan & 1-Click Photo Replacement
- Mode edit penuh (`/edit` & `/update`) untuk memperbarui data checklist, keterangan, maupun metadata.
- Tombol **"Ganti Foto Ini"** untuk penggantian foto bukti secara individual tanpa mengunggah ulang foto lainnya, disertai auto-regenerasi dokumen Word `.docx`.

### 4. Watermark Foto Otomatis & Ketahanan Draft Offline
- **Watermarking Gambar (`Pillow`)**: Setiap foto bukti yang diunggah otomatis diberi overlay teks informasi (`S/N | Tanggal | Lokasi`).
- **Autosave Draft Offline (`static/drafts.js`)**: Penyimpanan otomatis berbasis `localStorage` / `IndexedDB` dengan indikator banner kuning jika koneksi terputus di tengah pengujian.
- **Auto-Suggest Dropdown (`/api/suggestions`)**: Autocomplete otomatis untuk kolom Lokasi, Petugas Penguji, Saksi, dan Tipe Perangkat.

### 5. Visual Dashboard Analytics & Filter Lanjutan (`analytics.py`)
- Donut chart rasio PASS/FAIL total.
- Bar chart tren kapasitas pengujian harian (14 Hari terakhir).
- Visual progress bar ranking item checklist yang paling sering gagal.
- Toolbar Filter Lanjutan: Filter berdasarkan Status (PASS/FAIL), Vendor, Rentang Waktu (Hari Ini, 7 Hari, 30 Hari), dan Model Perangkat.

### 6. Cetak, Komparasi, & Export Excel Multi-Sheet
- **Export Excel (`openpyxl`)**: Menghasilkan file `.xlsx` 4-sheet (*Ringkasan Semua Vendor*, *Fortinet*, *Cisco*, *VeloCloud*).
- **Cetak Siap Pakai (Web Print)**: Fitur cetak tunggal maupun cetak masal langsung dari browser tanpa perlu membuka Microsoft Word.
- **Komparasi Laporan**: Membandingkan hasil uji antardevices atau antarversi pengujian.

### 7. Keamanan PIN Supervisor
- Penghapusan laporan (`/delete`) dilindungi PIN supervisor di tingkat server.
- PIN default: `1234` — dapat diganti melalui file `data/supervisor_pin.txt`.

---

## 🛠️ Cara Menjalankan

### Di Windows:
Klik dua kali **`start.bat`**, **atau** dari Windows PowerShell:

```powershell
cd sdwan-testing-app
.\.venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000 --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
```

### Di macOS / Linux:
Klik dua kali `start.command` di Finder, atau dari terminal:

```bash
cd sdwan-testing-app
.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 \
  --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
```

Lalu buka `https://localhost:8000`. Operator (HP/tablet/laptop) di Wi-Fi yang sama dapat membuka `https://<IP-laptop-ini>:8000` dengan melakukan scan **QR Code** yang tampil di halaman utama aplikasi.

#### Catatan Akses Jaringan & Sertifikat SSL:
- Aplikasi berjalan via **HTTPS (Self-Signed Certificate)** wajib agar browser mengizinkan akses kamera HP sebagai barcode scanner. Saat pertama membuka, pilih *Advanced / Lanjutkan (Proceed)*.
- `start.command` / `start.ps1` otomatis memperbarui sertifikat jika IP laptop berubah.

---

## 📋 Alur Kerja Operator

1. **Scan S/N** perangkat via scanner hardware IWare atau Kamera HP di halaman utama.
2. System secara otomatis mendeteksi Vendor (Fortinet / Cisco / VeloCloud). Jika S/N sudah ada, sistem menampilkan prompt opsi *Re-test*, *Edit*, atau *Lihat Riwayat*.
3. Isi checklist item uji (**OK / NOT OK**) beserta keterangan pendukung jika NOT OK.
4. Unggah foto bukti untuk setiap seksi foto. Foto otomatis diperkecil & diberi watermark.
5. Klik **Simpan Pengujian** → Dokumen Berita Acara Word (`.docx`) langsung dibuat, status PASS/FAIL dihitung otomatis (PASS jika seluruh item OK).
6. Data lokasi, petugas, dan saksi diingat otomatis untuk pengujian berikutnya.

---

## 📁 Struktur File & Folder

| Path | Isi / Fungsi |
|---|---|
| `app.py` | FastAPI Application & Web Routes |
| `checklist.py` | Registry Metadata Vendor, Item Uji & Seksi Foto Dynamic |
| `report.py` | Generator Laporan Word `.docx` & Layout Tanda Tangan 2x2 |
| `analytics.py` | Endpoint API Analytics Dashboard & Kalkulasi Statistik |
| `db.py` | Skema SQLite DB & Engine Migrasi Otomatis |
| `ba_template_fortinet.docx` | Template Berita Acara Word Fortinet |
| `ba_template_cisco.docx` | Template Berita Acara Word Cisco |
| `ba_template_velocloud.docx` | Template Berita Acara Word VeloCloud |
| `static/` | Stylesheet (`style.css`), Scanner (`scanner.js`), Draft Auto-save (`drafts.js`) |
| `templates/` | Template HTML Jinja2 (`index.html`, `form.html`, `edit.html`, `detail.html`, `duplicate_prompt.html`, `print.html`, `qr.html`) |
| `data/testing.db` | File Database SQLite Utama |
| `data/evidence/` | Folder Penyimpanan Bukti Foto & File `.docx` per Perangkat |
| `data/supervisor_pin.txt` | File Konfigurasi PIN Supervisor |

---

## 💾 Backup & Pemeliharaan

- **Backup Data**: Cukup salin/backup folder `data/` (berisi database SQLite `testing.db` dan seluruh folder bukti `evidence/`).
- **Ganti PIN Supervisor**: Edit isi file `data/supervisor_pin.txt` (satu baris teks PIN baru) tanpa perlu me-restart server.
- **Foto Evidence**: Kompresi otomatis (max 1600px JPEG) menjaga efisiensi penyimpanan storage lokal.
