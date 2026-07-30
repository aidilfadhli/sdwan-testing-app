VENDOR_REGISTRY = {
    "fortinet": {
        "id": "fortinet",
        "name": "Fortinet SD-WAN Edge",
        "badge_color": "nok", # red/orange badge style
        "template_file": "ba_template_fortinet.docx",
        "sn_prefixes": ["FGT", "FG"],
        "items": [
            {
                "key": "item1",
                "nama": "Verifikasi Model Perangkat",
                "prosedur": "Cek label/tipe perangkat pada casing dan bandingkan dengan Purchase Order (PO); pastikan model perangkat (mis. FortiGate 40F) sesuai PO.",
                "category": "Documentation & Model",
            },
            {
                "key": "item2",
                "nama": "Verifikasi Serial Number (S/N)",
                "prosedur": "Cek label S/N pada perangkat dan cocokkan dengan dokumen Delivery Order; pastikan S/N sesuai dokumen Delivery Order.",
                "category": "Documentation & Model",
            },
            {
                "key": "item3",
                "nama": "Pemeriksaan Kondisi Fisik",
                "prosedur": "Cek kondisi casing, port, dan kelengkapan aksesoris perangkat; pastikan tidak terdapat kerusakan fisik.",
                "category": "Physical & Power",
            },
            {
                "key": "item4",
                "nama": "Power On Test",
                "prosedur": "Hidupkan perangkat, amati proses booting dan indikator LED (Power, Status, Alarm); pastikan perangkat booting normal tanpa alarm.",
                "category": "Physical & Power",
            },
            {
                "key": "item5",
                "nama": "Verifikasi Versi FortiOS",
                "prosedur": "Akses GUI/CLI perangkat, cek versi firmware pada Dashboard/System Information atau CLI 'get system status'; pastikan versi FortiOS sesuai standar implementasi.",
                "category": "Firmware & System",
            },
            {
                "key": "item6",
                "nama": "Uji Interface LAN",
                "prosedur": "Colok kabel UTP dari port LAN (port1/2/3) ke laptop, set IP satu network, cek status interface pada LED Fortinet pastikan menyala dan uji ping dua arah; pastikan status Up.",
                "category": "Interface & SFP",
            },
        ],
        "photo_sections": [
            {"key": "fisik", "judul": "Kondisi Fisik Perangkat (tampak depan, belakang, serial number)"},
            {"key": "led", "judul": "Power On Test & Indikator LED"},
            {"key": "fortios", "judul": "Verifikasi Versi FortiOS (GUI/CLI)"},
            {"key": "kabel", "judul": "Koneksi Fisik Kabel UTP"},
            {"key": "interface", "judul": "Status Interface (GUI/CLI)"},
            {"key": "ping", "judul": "Hasil Uji Ping (Konektivitas)"},
        ],
    },
    "cisco": {
        "id": "cisco",
        "name": "Cisco SD-WAN Edge (ISR1100 Series)",
        "badge_color": "ok", # blue/green badge style
        "template_file": "ba_template_cisco.docx",
        "sn_prefixes": ["FGL", "FOC"],
        "items": [
            {
                "key": "item1",
                "nama": "Verifikasi Model Perangkat",
                "prosedur": "Cek label/tipe perangkat pada casing dan bandingkan dengan Purchase Order (PO), pastikan model perangkat sesuai dengan model yang tercantum pada PO.",
                "category": "Documentation & Model",
            },
            {
                "key": "item2",
                "nama": "Verifikasi Serial Number (S/N)",
                "prosedur": "Cek label S/N pada perangkat dan cocokkan dengan dokumen Delivery Order. Pastikan S/N sesuai.",
                "category": "Documentation & Model",
            },
            {
                "key": "item3",
                "nama": "Pemeriksaan Kondisi Fisik",
                "prosedur": "Cek kondisi casing, port, dan kelengkapan aksesoris perangkat; pastikan tidak terdapat kerusakan fisik.",
                "category": "Physical & Power",
            },
            {
                "key": "item4",
                "nama": "Power On Test",
                "prosedur": "Hidupkan perangkat, amati proses booting dan indikator LED. Pastikan perangkat menyala normal tanpa alarm.",
                "category": "Physical & Power",
            },
            {
                "key": "item5",
                "nama": "Verifikasi Versi Software (IOS XE SD-WAN)",
                "prosedur": "Akses CLI via console/terminal, jalankan perintah 'show version'. Pastikan versi IOS XE SD-WAN sesuai standar implementasi.",
                "category": "Firmware & System",
            },
            {
                "key": "item6",
                "nama": "Uji Interface LAN",
                "prosedur": "Colok kabel UTP dari port LAN ke laptop, set IP satu network, cek status dengan 'show ip interface brief' dan uji ping dua arah. Pastikan status interface LAN Up/aktif.",
                "category": "Interface & SFP",
            },
        ],
        "photo_sections": [
            {"key": "fisik", "judul": "Kondisi Fisik Perangkat (tampak depan, belakang, serial number)"},
            {"key": "led", "judul": "Power On Test & Indikator LED"},
            {"key": "os", "judul": "Verifikasi Versi Software via CLI (show version)"},
            {"key": "kabel", "judul": "Koneksi Kabel UTP ke Laptop per Port"},
            {"key": "interface", "judul": "Status Interface (show ip interface brief)"},
            {"key": "ping", "judul": "Hasil Uji Ping (Konektivitas)"},
        ],
    },
    "velocloud": {
        "id": "velocloud",
        "name": "VMware (VeloCloud) SD-WAN Edge",
        "badge_color": "warning", # purple/yellow badge style
        "template_file": "ba_template_velocloud.docx",
        "sn_prefixes": ["VC"],
        "items": [
            {
                "key": "item1",
                "nama": "Verifikasi Model Perangkat",
                "prosedur": "Cek label/tipe perangkat pada casing dan bandingkan dengan Purchase Order (PO); pastikan model Edge (mis. Edge 710) sesuai PO.",
                "category": "Documentation & Model",
            },
            {
                "key": "item2",
                "nama": "Verifikasi Serial Number (S/N)",
                "prosedur": "Cek label S/N pada perangkat dan cocokkan dengan dokumen Delivery Order; pastikan S/N sesuai.",
                "category": "Documentation & Model",
            },
            {
                "key": "item3",
                "nama": "Pemeriksaan Kondisi Fisik",
                "prosedur": "Cek kondisi casing, port, dan kelengkapan aksesoris perangkat; pastikan tidak terdapat kerusakan fisik.",
                "category": "Physical & Power",
            },
            {
                "key": "item4",
                "nama": "Power On Test",
                "prosedur": "Hidupkan perangkat, amati proses booting; pastikan perangkat booting normal tanpa alarm, pastikan seluruh LED menunjukkan status normal.",
                "category": "Physical & Power",
            },
            {
                "key": "item5",
                "nama": "Verifikasi Versi Software Edge",
                "prosedur": "Cek versi software Edge melalui GUI lokal; pastikan versi sesuai standar implementasi.",
                "category": "Firmware & System",
            },
            {
                "key": "item6",
                "nama": "Uji Interface SFP",
                "prosedur": "Colok modul SFP beserta kabel fiber optik pada port SFP; amati status interface pada GUI lokal; pastikan status Up.",
                "category": "Interface & SFP",
            },
            {
                "key": "item7",
                "nama": "Uji Interface GE",
                "prosedur": "Colok kabel UTP dari port LAN ke laptop; amati status interface pada GUI lokal; pastikan status Up.",
                "category": "Interface & SFP",
            },
        ],
        "photo_sections": [
            {"key": "fisik", "judul": "Kondisi Fisik Perangkat (tampak depan, belakang, serial number)"},
            {"key": "led", "judul": "Power On Test & Indikator LED"},
            {"key": "os", "judul": "Verifikasi Versi Software via Local GUI"},
            {"key": "kabel", "judul": "Koneksi Kabel UTP dan SFP ke Laptop per Port"},
            {"key": "interface", "judul": "Status Link Interface (Local GUI/VCO)"},
            {"key": "ping", "judul": "Hasil Uji Ping (Konektivitas)"},
        ],
    },
}


def get_vendor_spec(vendor_id: str | None = None) -> dict:
    """Ambil spesifikasi vendor berdasarkan ID, default ke fortinet jika tidak valid/kosong."""
    if not vendor_id:
        return VENDOR_REGISTRY["fortinet"]
    key = str(vendor_id).strip().lower()
    return VENDOR_REGISTRY.get(key, VENDOR_REGISTRY["fortinet"])


def detect_vendor_by_sn(sn: str) -> str:
    """Deteksi vendor otomatis berdasarkan prefix Serial Number."""
    sn_clean = (sn or "").strip().upper()
    all_prefixes = []
    for v_id, spec in VENDOR_REGISTRY.items():
        for prefix in spec.get("sn_prefixes", []):
            all_prefixes.append((prefix.upper(), v_id))
    # Urgent: sort by longest prefix first so 'FGL' matches before 'FG'
    all_prefixes.sort(key=lambda x: len(x[0]), reverse=True)

    for prefix, v_id in all_prefixes:
        if sn_clean.startswith(prefix):
            return v_id
    return "fortinet"


# Fallback kontstanta untuk kompatibilitas fungsi legacy
CHECKLIST_ITEMS = VENDOR_REGISTRY["fortinet"]["items"]
PHOTO_SECTIONS = VENDOR_REGISTRY["fortinet"]["photo_sections"]

