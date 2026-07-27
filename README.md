# Mass Testing SD-WAN — Form Digital Berita Acara Uji Fungsi

Aplikasi web lokal untuk uji fungsi massal perangkat Fortinet SD-WAN Edge di gudang.
Menggantikan pengisian manual dokumen *Berita Acara Uji Fungsi*: operator scan S/N,
isi checklist 6 item (OK / NOT OK), unggah foto bukti, dan aplikasi otomatis:

- menyimpan semua hasil ke database (SQLite),
- menyusun folder bukti per perangkat (`data/evidence/<SN>_r<id>/`),
- **menghasilkan Berita Acara .docx** persis format dokumen asli (template: `ba_template.docx`),
- menyediakan **export Excel** register seluruh perangkat (tombol *Export Excel*).

## Cara menjalankan

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

Lalu buka `https://localhost:8000`. Operator (HP/tablet/laptop) di Wi-Fi yang sama
membuka `https://<IP-laptop-ini>:8000` — alamat + **QR code** tampil di halaman utama
aplikasi, operator cukup scan QR itu dengan kamera HP.

Catatan akses jaringan:

- Aplikasi berjalan **HTTPS dengan sertifikat self-signed** (wajib, agar kamera HP
  bisa dipakai sebagai scanner barcode). Saat pertama membuka, browser menampilkan
  peringatan sertifikat → pilih *Advanced / Lanjutkan* (sekali saja per HP).
- `start.command` otomatis membuat ulang sertifikat bila IP laptop berubah.
- Jika HP tidak bisa membuka: pastikan satu Wi-Fi dengan laptop, dan bila macOS
  menanyakan *"Allow Python to accept incoming network connections?"* pilih **Allow**
  (System Settings → Network → Firewall bila perlu).

## Scan barcode

Dua cara, keduanya menuju kolom S/N yang sama:

1. **Scanner IWare** — bekerja seperti keyboard; set suffix *Enter/CR* agar
   hasil scan otomatis submit.
2. **Kamera HP** — tombol **📷 Kamera** di halaman utama / form membuka kamera dan
   membaca barcode label (Code-128, EAN, QR, dll.) langsung di browser, tanpa
   install aplikasi.

## Alur kerja operator

1. **Scan S/N** dengan scanner IWare pada kolom besar di halaman utama
   (scanner bekerja sebagai keyboard; set suffix *Enter/CR* agar otomatis submit).
   - S/N baru → form uji terbuka dengan S/N terisi.
   - S/N sudah pernah diuji → halaman hasil terbuka (ada tombol *Uji Ulang*).
2. Isi checklist 6 item dengan tombol **OK / NOT OK** + keterangan bila perlu.
3. Unggah foto per bagian bukti (dari HP: langsung buka kamera; boleh multi-foto).
4. **Simpan** → BA .docx langsung dibuat; status PASS/FAIL otomatis
   (PASS hanya jika seluruh 6 item OK).
5. Nilai Lokasi / Petugas / Saksi diingat otomatis di perangkat operator.

## Struktur

| Path | Isi |
|---|---|
| `app.py` | Aplikasi web (FastAPI) |
| `checklist.py` | Definisi 6 item uji & 5 seksi foto (ubah di sini bila checklist berubah) |
| `report.py` | Pengisian Berita Acara .docx dari template |
| `ba_template.docx` | Template BA (salinan dokumen asli — jangan diubah strukturnya) |
| `db.py` | Skema database SQLite |
| `data/testing.db` | Database hasil uji |
| `data/evidence/` | Folder bukti per perangkat (foto + BA .docx) |

**Backup:** cukup salin folder `data/` (berisi seluruh database + bukti).

## Cetak (satu atau banyak laporan sekaligus)

Tombol 🖨 **Print** (di daftar, halaman hasil, atau baris masing-masing laporan)
membuka tab baru berisi laporan dalam format siap cetak — dialog Print browser
langsung terbuka, tanpa perlu membuka Word.

- Di daftar utama: centang laporan yang diinginkan → **Print Terpilih**,
  atau langsung **Print Semua** untuk seluruh daftar yang tampil.
- Setiap laporan dimulai di halaman baru saat dicetak; foto diambil langsung dari
  folder bukti (tidak digabung jadi satu file besar), jadi tetap ringan meski
  mencetak puluhan/ratusan laporan sekaligus.

## Hapus laporan & PIN supervisor

Tombol 🗑 (di daftar & halaman hasil) menghapus laporan beserta seluruh foto dan
BA-nya. Penghapusan **membutuhkan PIN supervisor** yang diverifikasi di server.

- PIN default: `1234` — **segera ganti**: edit file `data/supervisor_pin.txt`
  (isi satu baris berisi PIN), tidak perlu restart aplikasi.

## Catatan operasional

- Foto otomatis diperkecil (maks 1600 px, JPEG) agar file BA dan storage hemat.
- Aplikasi tanpa login — jalankan hanya di jaringan gudang yang terkendali.
- Kapasitas: SQLite + file lokal aman untuk puluhan ribu perangkat.
