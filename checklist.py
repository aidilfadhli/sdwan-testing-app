"""Definisi checklist uji fungsi dan seksi foto — mengikuti dokumen
Berita Acara Uji Fungsi SD-WAN Edge Platform Fortinet."""

CHECKLIST_ITEMS = [
    {
        "key": "item1",
        "nama": "Verifikasi Model Perangkat",
        "prosedur": "Cek label/tipe perangkat pada casing dan bandingkan dengan Purchase Order (PO); pastikan model perangkat (mis. FortiGate 40F) sesuai PO.",
    },
    {
        "key": "item2",
        "nama": "Verifikasi Serial Number (S/N)",
        "prosedur": "Cek label S/N pada perangkat dan cocokkan dengan dokumen Delivery Order; pastikan S/N sesuai dokumen Delivery Order.",
    },
    {
        "key": "item3",
        "nama": "Pemeriksaan Kondisi Fisik",
        "prosedur": "Cek kondisi casing, port, dan kelengkapan aksesoris perangkat; pastikan tidak terdapat kerusakan fisik.",
    },
    {
        "key": "item4",
        "nama": "Power On Test",
        "prosedur": "Hidupkan perangkat, amati proses booting dan indikator LED (Power, Status, Alarm); pastikan perangkat booting normal tanpa alarm.",
    },
    {
        "key": "item5",
        "nama": "Verifikasi Versi FortiOS",
        "prosedur": "Akses GUI/CLI perangkat, cek versi firmware pada Dashboard/System Information atau CLI 'get system status'; pastikan versi FortiOS sesuai standar implementasi.",
    },
    {
        "key": "item6",
        "nama": "Uji Interface LAN",
        "prosedur": "Colok kabel UTP dari port LAN (port1/2/3) ke laptop, set IP satu network, cek status interface pada LED Fortinet pastikan menyala dan uji ping dua arah; pastikan status Up.",
    },
]

# Seksi foto — urutan sama dengan tabel foto pada dokumen BA (tabel 2..6)
PHOTO_SECTIONS = [
    {"key": "fisik", "judul": "Kondisi Fisik Perangkat (tampak depan, belakang, serial number)"},
    {"key": "led", "judul": "Power On Test & Indikator LED"},
    {"key": "fortios", "judul": "Verifikasi Versi FortiOS (GUI/CLI)"},
    {"key": "interface", "judul": "Koneksi Fisik Kabel UTP & Status Interface"},
    {"key": "ping", "judul": "Hasil Uji Ping (Konektivitas)"},
]
