# BERITA ACARA UJI FUNGSI PERANGKAT

> **Catatan konversi:** Dokumen sumber berisi 3 template (Cisco, Fortinet, VMware/VeloCloud), yang masing-masing diikuti oleh contoh pengisian. Terdapat beberapa inkonsistensi antara *template* dan *contoh* (misalnya jumlah baris checklist berbeda — contoh Fortinet menambahkan item Uji Koneksi ke FortiGuard, WAN1, WAN2, dan LAN; contoh VeloCloud menambahkan item GE5/GE6). Sesuai arahan, dokumen ini menggunakan **template asli sebagai baseline**, bukan versi contoh.

---

## 1. Cisco SD-WAN Edge

### I. Identitas Perangkat & Pengujian

| Field | Isi |
|---|---|
| Hostname | |
| Serial Number (S/N) | |
| Nomor Aset / BA | |
| Lokasi Pengujian | |
| Tanggal Pengujian | |
| Petugas Penguji | |

### II. Checklist Uji Fungsi

*Beri tanda pada kolom Hasil dengan OK / NOT OK sesuai temuan di lapangan.*

| No | Item Pengujian | Prosedur / Cara Uji | Hasil | Keterangan |
|---|---|---|---|---|
| 1 | Verifikasi Model Perangkat | Cek label/tipe perangkat pada casing dan bandingkan dengan Purchase Order (PO), pastikan model perangkat sesuai dengan model yang tercantum pada PO. | | |
| 2 | Verifikasi Serial Number (S/N) | Cek label S/N pada perangkat dan cocokkan dengan dokumen Delivery Order. Pastikan S/N sesuai. | | |
| 3 | Pemeriksaan Kondisi Fisik | Cek kondisi casing, port, dan kelengkapan aksesoris perangkat; pastikan tidak terdapat kerusakan fisik. | | |
| 4 | Power On Test | Hidupkan perangkat, amati proses booting dan indikator LED. Pastikan perangkat menyala normal tanpa alarm. | | |
| 5 | Verifikasi Versi Software (IOS XE SD-WAN) | Akses CLI via console/terminal, jalankan perintah 'show version'. Pastikan versi IOS XE SD-WAN sesuai standar implementasi. | | |
| 6 | Uji Interface LAN | Colok kabel UTP dari port LAN ke laptop, set IP satu network, cek status dengan 'show ip interface brief' dan uji ping dua arah. Pastikan status interface LAN Up/aktif. | | |

### III. Lampiran Dokumentasi Foto

*Sisipkan foto hasil pengujian pada masing-masing kotak di bawah ini.*

1. **Kondisi Fisik Perangkat** (tampak depan, belakang, serial number)
   `[ Sisipkan foto di sini ]`
   *Gambar 1. Kondisi fisik perangkat Cisco ISR1100-4G*

2. **Power On Test & Indikator LED**
   `[ Sisipkan foto di sini ]`
   *Gambar 2. Kondisi lampu LED indikator saat perangkat berhasil booting normal.*

3. **Verifikasi Versi Software via CLI**
   `[ Sisipkan foto di sini ]`
   *Gambar 3. Tampilan output perintah 'show version' pada terminal console.*

4. **Koneksi Kabel UTP ke Laptop per Port**
   `[ Sisipkan foto di sini ]`
   *Gambar 4. Kabel UTP terpasang dari port perangkat ke laptop*

5. **Status Interface**
   `[ Sisipkan foto di sini ]`
   *Gambar 5. Tampilan output 'show ip interface brief' yang menunjukkan status interface Up.*

6. **Hasil Uji Ping (Konektivitas)**
   `[ Sisipkan foto di sini ]`
   *Gambar 6. Hasil ping sukses dua arah pada layar terminal/CMD*

### IV. Catatan Tambahan

```



```

**Petugas Penguji**
( __________________________ )
( Nama / NIP )

**Mengetahui / Saksi**
( __________________________ )
( Nama / NIP )

---

## 2. Fortinet SD-WAN Edge

### I. Identitas Perangkat & Pengujian

| Field | Isi |
|---|---|
| Hostname | |
| Serial Number (S/N) | |
| Nomor Aset / BA | |
| Lokasi Pengujian | |
| Tanggal Pengujian | |
| Petugas Penguji | |

### II. Checklist Uji Fungsi

*Beri tanda pada kolom Hasil dengan OK / NOT OK sesuai temuan di lapangan.*

| No | Item Pengujian | Prosedur / Cara Uji | Hasil | Keterangan |
|---|---|---|---|---|
| 1 | Verifikasi Model Perangkat | Cek label/tipe perangkat pada casing dan bandingkan dengan Purchase Order (PO); pastikan model perangkat (mis. FortiGate 40F) sesuai PO. | | |
| 2 | Verifikasi Serial Number (S/N) | Cek label S/N pada perangkat dan cocokkan dengan dokumen Delivery Order; pastikan S/N sesuai dokumen Delivery Order. | | |
| 3 | Pemeriksaan Kondisi Fisik | Cek kondisi casing, port, dan kelengkapan aksesoris perangkat; pastikan tidak terdapat kerusakan fisik. | | |
| 4 | Power On Test | Hidupkan perangkat, amati proses booting dan indikator LED (Power, Status, Alarm); pastikan perangkat booting normal tanpa alarm. | | |
| 5 | Verifikasi Versi FortiOS | Akses GUI/CLI perangkat, cek versi firmware pada Dashboard/System Information atau CLI 'get system status'; pastikan versi FortiOS sesuai standar implementasi. | | |
| 6 | Uji Interface LAN | Colok kabel UTP dari port LAN (port1/2/3) ke laptop, set IP satu network, cek status interface pada led fortinet pastikan menyala dan uji ping dua arah; pastikan status Up. | | |

### III. Lampiran Dokumentasi Foto

*Sisipkan foto hasil pengujian pada masing-masing kotak di bawah ini.*

1. **Kondisi Fisik Perangkat** (tampak depan, belakang, serial number)
   `[ Sisipkan foto di sini ]`
   *Gambar 1. Kondisi fisik perangkat Fortinet FortiGate*

2. **Power On Test & Indikator LED**
   `[ Sisipkan foto di sini ]`
   *Gambar 2. Kondisi lampu LED (Power, Status) menyala normal tanpa alarm.*

3. **Verifikasi Versi FortiOS (GUI/CLI)**
   `[ Sisipkan foto di sini ]`
   *Gambar 3. Tampilan Dashboard/System Information (GUI) atau perintah 'get system status' (CLI).*

4. **Koneksi Fisik Kabel UTP**
   `[ Sisipkan foto di sini ]`
   *Gambar 4. Kabel UTP terpasang pada port LAN.*

5. **Status Interface**
   `[ Sisipkan foto di sini ]`
   *Gambar 5. Tampilan output yang menunjukkan status interface Up.*

6. **Hasil Uji Ping (Konektivitas)**
   `[ Sisipkan foto di sini ]`
   *Gambar 6. Hasil ping sukses dua arah pada layar terminal/CMD*

### IV. Catatan Tambahan

```



```

**Petugas Penguji**
( __________________________ )
( Nama / NIP )

**Mengetahui / Saksi**
( __________________________ )
( Nama / NIP )

---

## 3. VMware (VeloCloud) SD-WAN Edge

### I. Identitas Perangkat & Pengujian

| Field | Isi |
|---|---|
| Hostname | |
| Serial Number (S/N) | |
| Nomor Aset / BA | |
| Lokasi Pengujian | |
| Tanggal Pengujian | |
| Petugas Penguji | |

### II. Checklist Uji Fungsi

*Beri tanda pada kolom Hasil dengan OK / NOT OK sesuai temuan di lapangan.*

| No | Item Pengujian | Prosedur / Cara Uji | Hasil | Keterangan |
|---|---|---|---|---|
| 1 | Verifikasi Model Perangkat | Cek label/tipe perangkat pada casing dan bandingkan dengan Purchase Order (PO); pastikan model Edge (mis. Edge 710) sesuai PO. | | |
| 2 | Verifikasi Serial Number (S/N) | Cek label S/N pada perangkat dan cocokkan dengan dokumen Delivery Order; pastikan S/N sesuai. | | |
| 3 | Pemeriksaan Kondisi Fisik | Cek kondisi casing, port, dan kelengkapan aksesoris perangkat; pastikan tidak terdapat kerusakan fisik. | | |
| 4 | Power On Test | Hidupkan perangkat, amati proses booting; pastikan perangkat booting normal tanpa alarm, pastikan seluruh LED menunjukkan status normal. | | |
| 5 | Verifikasi Versi Software Edge | Cek versi software Edge melalui GUI lokal; pastikan versi sesuai standar implementasi. | | |
| 6 | Uji Interface SFP | Colok modul SFP beserta kabel fiber optik pada port SFP; amati status interface pada GUI lokal; pastikan status Up | | |
| 7 | Uji Interface GE | Colok kabel UTP dari port LAN ke laptop; amati status interface pada GUI lokal; pastikan status Up. | | |

### III. Lampiran Dokumentasi Foto

*Sisipkan foto hasil pengujian pada masing-masing kotak di bawah ini.*

1. **Kondisi Fisik Perangkat** (tampak depan, belakang, serial number)
   `[ Sisipkan foto di sini ]`
   *Gambar 1. Kondisi fisik perangkat VeloCloud Edge*

2. **Power On Test & Indikator LED**
   `[ Sisipkan foto di sini ]`
   *Gambar 2. Kondisi lampu LED (Power, Status, Link) menyala normal.*

3. **Verifikasi Versi Software via Local GUI**
   `[ Sisipkan foto di sini ]`
   *Gambar 3. Tampilan informasi versi software pada halaman web manajemen lokal Edge.*

4. **Koneksi Kabel UTP dan SFP ke Laptop per Port**
   `[ Sisipkan foto di sini ]`
   *Gambar 4. Kabel UTP terpasang dari port perangkat ke laptop/sumber jaringan.*

5. **Status Link Interface (Local GUI/VCO)**
   `[ Sisipkan foto di sini ]`
   *Gambar 5. Tampilan status interface WAN/LAN yang terdeteksi 'Up'.*

6. **Hasil Uji Ping (Konektivitas)**
   `[ Sisipkan foto di sini ]`
   *Gambar 6. Hasil ping sukses dua arah pada layar CMD laptop.*

### IV. Catatan Tambahan

```



```

**Petugas Penguji**
( __________________________ )
( Nama / NIP )

**Mengetahui / Saksi**
( __________________________ )
( Nama / NIP )
