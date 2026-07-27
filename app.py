"""Aplikasi Mass Testing SD-WAN — form digital Berita Acara Uji Fungsi.

Jalankan:  .venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Operator membuka lewat browser HP/laptop di jaringan yang sama.
Scanner barcode IWare bekerja sebagai keyboard: scan S/N pada kolom pencarian.
"""

import asyncio
import io
import json
import logging
import shutil
import socket
import threading
import zipfile
from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from starlette.datastructures import UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image

from checklist import CHECKLIST_ITEMS, PHOTO_SECTIONS
from db import DATA_DIR, EVIDENCE_DIR, evidence_dir, get_conn
from report import generate_ba

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Mass Testing SD-WAN")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/evidence", StaticFiles(directory=EVIDENCE_DIR), name="evidence")

templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.globals.update(CHECKLIST_ITEMS=CHECKLIST_ITEMS, PHOTO_SECTIONS=PHOTO_SECTIONS)

MAX_DIM = 1600  # foto diperkecil agar BA & storage hemat

# PIN supervisor untuk hapus laporan — ganti dengan mengedit file data/supervisor_pin.txt
PIN_FILE = DATA_DIR / "supervisor_pin.txt"
SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "auto_backup_enabled": False,
    "auto_backup_interval": "daily",
    "last_auto_backup_time": 0,
}

INTERVAL_SECONDS = {
    "6h": 6 * 3600,
    "12h": 12 * 3600,
    "daily": 24 * 3600,
    "weekly": 7 * 24 * 3600,
    "monthly": 30 * 24 * 3600,
}

logger = logging.getLogger("uvicorn.error")

async def scheduled_backup_loop():
    """Background task to perform periodic auto-backups."""
    while True:
        try:
            st = get_settings()
            if st.get("auto_backup_enabled"):
                interval_key = st.get("auto_backup_interval", "daily")
                if interval_key in INTERVAL_SECONDS:
                    target_sec = INTERVAL_SECONDS[interval_key]
                    last_time = float(st.get("last_auto_backup_time", 0))
                    now = datetime.now().timestamp()
                    if now - last_time >= target_sec:
                        run_backup_in_background()
                        save_settings_data({"last_auto_backup_time": now})
                        logger.info(f"[Auto-Backup] Periodic backup started for interval: {interval_key}")
        except Exception as e:
            logger.error(f"[Auto-Backup] Error in scheduled loop: {e}")
        
        await asyncio.sleep(60)

@app.on_event("startup")
def start_backup_scheduler():
    asyncio.create_task(scheduled_backup_loop())


def get_settings() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.write_text(json.dumps(DEFAULT_SETTINGS, indent=2))
        return DEFAULT_SETTINGS.copy()
    try:
        data = json.loads(SETTINGS_FILE.read_text())
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings_data(new_settings: dict) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    current = get_settings()
    current.update(new_settings)
    SETTINGS_FILE.write_text(json.dumps(current, indent=2))
    return current


BACKUP_PROGRESS = {
    "status": "idle",
    "progress": 0,
    "message": "Siap",
    "folder": "",
    "filename": ""
}


def create_backup_zip() -> tuple[Path, str, str]:
    """Membuat backup ZIP di folder BACKUP/<timestamp>/ dan mengembalikan (zip_path, folder_name, zip_filename)."""
    global BACKUP_PROGRESS
    BACKUP_PROGRESS.update({
        "status": "running",
        "progress": 5,
        "message": "Menyiapkan berkas backup...",
        "folder": "",
        "filename": ""
    })

    BACKUP_BASE_DIR = BASE_DIR / "BACKUP"
    BACKUP_BASE_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    folder_name = now.strftime("%Y-%m-%d_%H-%M-%S")
    target_dir = BACKUP_BASE_DIR / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    zip_filename = f"backup_sdwan_{folder_name}.zip"
    zip_path = target_dir / zip_filename

    files_to_zip = []
    seen_arcs = set()
    if DATA_DIR.exists():
        for file_path in sorted(DATA_DIR.rglob("*")):
            if file_path.is_file() and not file_path.name.endswith(".tmp") and not file_path.name.endswith(".zip"):
                arcname = str(file_path.relative_to(DATA_DIR))
                if arcname not in seen_arcs:
                    seen_arcs.add(arcname)
                    files_to_zip.append((file_path, arcname))

    total_files = len(files_to_zip)
    BACKUP_PROGRESS.update({
        "progress": 15,
        "message": f"Mengompres {total_files} file data & foto..."
    })

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for idx, (fpath, arcname) in enumerate(files_to_zip, start=1):
            zf.write(fpath, arcname=arcname)
            pct = 15 + int((idx / max(total_files, 1)) * 80)
            BACKUP_PROGRESS.update({
                "progress": pct,
                "message": f"Memproses {idx}/{total_files} ({fpath.name})..."
            })

    BACKUP_PROGRESS.update({
        "status": "completed",
        "progress": 100,
        "message": "Backup selesai!",
        "folder": folder_name,
        "filename": zip_filename
    })

    return zip_path, folder_name, zip_filename


def supervisor_pin() -> str:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PIN_FILE.exists():
        PIN_FILE.write_text("1234\n")
    return PIN_FILE.read_text().strip()


def get_lan_ip() -> str:
    """IP laptop ini di jaringan Wi-Fi/LAN — untuk ditampilkan ke operator."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # tidak mengirim paket, hanya memilih interface
        return s.getsockname()[0]
    except OSError:
        return "localhost"
    finally:
        s.close()


def server_url(request: Request) -> str:
    port = request.url.port or (443 if request.url.scheme == "https" else 80)
    return f"{request.url.scheme}://{get_lan_ip()}:{port}"


def save_photo(upload: UploadFile, dest_dir: Path, name_base: str) -> str | None:
    raw = upload.file.read()
    if not raw:
        return None
    try:
        img = Image.open(io.BytesIO(raw))
        img = img.convert("RGB")
        img.thumbnail((MAX_DIM, MAX_DIM))
        filename = f"{name_base}.jpg"
        img.save(dest_dir / filename, "JPEG", quality=82)
    except Exception:
        # bukan format yang dikenali Pillow — simpan apa adanya
        ext = Path(upload.filename or "foto.bin").suffix or ".bin"
        filename = f"{name_base}{ext}"
        (dest_dir / filename).write_bytes(raw)
    return filename


def report_row(conn, report_id: int):
    return conn.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()


def photos_for(conn, report_id: int):
    rows = conn.execute(
        "SELECT section, filename FROM photos WHERE report_id=? ORDER BY id", (report_id,)
    ).fetchall()
    grouped: dict[str, list[str]] = {s["key"]: [] for s in PHOTO_SECTIONS}
    for r in rows:
        grouped.setdefault(r["section"], []).append(r["filename"])
    return grouped


def ba_filename(report) -> str:
    safe_sn = "".join(c for c in report["serial_number"] if c.isalnum() or c in "-_") or "NOSN"
    return f"BA_Uji_Fungsi_{safe_sn}.docx"


@app.get("/")
def index(request: Request, q: str = ""):
    conn = get_conn()
    if q:
        rows = conn.execute(
            "SELECT * FROM reports WHERE serial_number LIKE ? ORDER BY id DESC",
            (f"%{q.strip()}%",),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM reports ORDER BY id DESC LIMIT 200").fetchall()
    stats = conn.execute(
        "SELECT COUNT(*) AS total,"
        " SUM(CASE WHEN status='PASS' THEN 1 ELSE 0 END) AS lulus,"
        " SUM(CASE WHEN status='FAIL' THEN 1 ELSE 0 END) AS gagal"
        " FROM reports"
    ).fetchone()
    conn.close()
    return templates.TemplateResponse(
        request, "index.html",
        {"rows": rows, "stats": stats, "q": q, "server_url": server_url(request)},
    )


@app.get("/qr")
def qr_code(request: Request):
    """QR berisi alamat aplikasi — operator scan dengan kamera HP untuk membuka."""
    import qrcode

    img = qrcode.make(server_url(request))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@app.get("/scan")
def scan(sn: str = ""):
    """Target scan barcode: jika S/N sudah pernah diuji buka hasilnya, jika belum buka form."""
    sn = sn.strip()
    if not sn:
        return RedirectResponse("/", status_code=303)
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM reports WHERE serial_number=? ORDER BY id DESC LIMIT 1", (sn,)
    ).fetchone()
    conn.close()
    if row:
        return RedirectResponse(f"/device/{row['id']}", status_code=303)
    return RedirectResponse(f"/form?sn={sn}", status_code=303)


@app.get("/form")
def form(request: Request, sn: str = ""):
    st = get_settings()
    return templates.TemplateResponse(
        request, "form.html", {
            "sn": sn.strip(),
            "today": date.today().isoformat(),
            "default_petugas": st.get("default_petugas", ""),
            "default_lokasi": st.get("default_lokasi", ""),
        }
    )


@app.post("/submit")
async def submit(request: Request):
    async with request.form() as form_data:
        def val(key):
            v = form_data.get(key, "")
            return v.strip() if isinstance(v, str) else ""

        sn = val("serial_number")
        if not sn:
            return RedirectResponse("/form", status_code=303)

        hasil = {i: val(f"hasil{i}") for i in range(1, 7)}
        status = "PASS" if all(hasil[i] == "OK" for i in range(1, 7)) else "FAIL"

        conn = get_conn()
        cur = conn.execute(
            """INSERT INTO reports (serial_number, type_device, lokasi, tanggal,
                 petugas, saksi, saksi2, saksi3,
                 hasil1, ket1, hasil2, ket2, hasil3, ket3,
                 hasil4, ket4, hasil5, ket5, hasil6, ket6,
                 catatan, status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                sn, val("type_device"), val("lokasi"), val("tanggal"),
                val("petugas"), val("saksi"), val("saksi2"), val("saksi3"),
                hasil[1], val("ket1"), hasil[2], val("ket2"), hasil[3], val("ket3"),
                hasil[4], val("ket4"), hasil[5], val("ket5"), hasil[6], val("ket6"),
                val("catatan"), status,
            ),
        )
        report_id = cur.lastrowid
        dest = evidence_dir(report_id, sn)

        for section in PHOTO_SECTIONS:
            uploads = form_data.getlist(f"photo_{section['key']}")
            n = 0
            for up in uploads:
                if not isinstance(up, UploadFile) or not (up.filename or "").strip():
                    continue
                n += 1
                fname = save_photo(up, dest, f"{section['key']}_{n:02d}")
                if fname:
                    conn.execute(
                        "INSERT INTO photos (report_id, section, filename) VALUES (?,?,?)",
                        (report_id, section["key"], fname),
                    )
        conn.commit()

        report = report_row(conn, report_id)
        grouped = photos_for(conn, report_id)
        photos_paths = {k: [dest / f for f in v] for k, v in grouped.items()}
        generate_ba(dict(report), photos_paths, dest / ba_filename(report))
        conn.close()

        st_backup = get_settings()
        if st_backup.get("auto_backup_enabled") and st_backup.get("auto_backup_interval") == "on_submit":
            create_backup_zip()

    return RedirectResponse(f"/device/{report_id}", status_code=303)


@app.get("/device/{report_id}")
def device(request: Request, report_id: int):
    conn = get_conn()
    report = report_row(conn, report_id)
    if report is None:
        conn.close()
        return RedirectResponse("/", status_code=303)
    grouped = photos_for(conn, report_id)
    conn.close()
    folder = evidence_dir(report_id, report["serial_number"]).name
    return templates.TemplateResponse(
        request, "detail.html",
        {"r": report, "photos": grouped, "folder": folder, "ba_file": ba_filename(report)},
    )


@app.post("/device/{report_id}/delete")
def delete_report(report_id: int, pin: str = Form("")):
    """Hapus laporan beserta foto dan folder buktinya — butuh PIN supervisor."""
    import shutil

    if pin.strip() != supervisor_pin():
        return RedirectResponse(f"/device/{report_id}?err=pin", status_code=303)

    conn = get_conn()
    report = report_row(conn, report_id)
    if report is not None:
        folder = evidence_dir(report_id, report["serial_number"])
        conn.execute("DELETE FROM photos WHERE report_id=?", (report_id,))
        conn.execute("DELETE FROM reports WHERE id=?", (report_id,))
        conn.commit()
        shutil.rmtree(folder, ignore_errors=True)
    conn.close()
    return RedirectResponse("/", status_code=303)

@app.post("/bulk-delete")
def bulk_delete_report(pin: str = Form(""), ids: str = Form("")):
    import shutil
    if pin.strip() != supervisor_pin():
        return RedirectResponse("/?err=pin", status_code=303)

    id_list = [int(x) for x in ids.split(",") if x.strip().isdigit()]
    if not id_list:
        return RedirectResponse("/", status_code=303)

    conn = get_conn()
    placeholders = ",".join("?" * len(id_list))
    rows = conn.execute(f"SELECT id, serial_number FROM reports WHERE id IN ({placeholders})", id_list).fetchall()
    
    for report in rows:
        folder = evidence_dir(report["id"], report["serial_number"])
        shutil.rmtree(folder, ignore_errors=True)
        
    conn.execute(f"DELETE FROM photos WHERE report_id IN ({placeholders})", id_list)
    conn.execute(f"DELETE FROM reports WHERE id IN ({placeholders})", id_list)
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=303)


@app.get("/report/{report_id}")
def download_ba(report_id: int):
    conn = get_conn()
    report = report_row(conn, report_id)
    conn.close()
    if report is None:
        return RedirectResponse("/", status_code=303)
    path = evidence_dir(report_id, report["serial_number"]) / ba_filename(report)
    if not path.exists():
        return RedirectResponse(f"/device/{report_id}", status_code=303)
    return FileResponse(
        path, filename=ba_filename(report),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.get("/bulk-report")
def bulk_download_ba(ids: str = ""):
    import zipfile
    id_list = [int(x) for x in ids.split(",") if x.strip().isdigit()]
    if not id_list:
        return RedirectResponse("/", status_code=303)
        
    if len(id_list) == 1:
        return download_ba(id_list[0])
        
    conn = get_conn()
    placeholders = ",".join("?" * len(id_list))
    rows = conn.execute(f"SELECT * FROM reports WHERE id IN ({placeholders})", id_list).fetchall()
    conn.close()
    
    if not rows:
        return RedirectResponse("/", status_code=303)
        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for r in rows:
            path = evidence_dir(r["id"], r["serial_number"]) / ba_filename(r)
            if path.exists():
                zf.write(path, arcname=ba_filename(r))
                
    zip_buffer.seek(0)
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=Berita_Acara_SDWAN_{now_str}.zip"}
    )


@app.get("/api/search")
def api_search(q: str = ""):
    if not q.strip():
        return {"results": []}
    conn = get_conn()
    q_like = f"%{q.strip()}%"
    rows = conn.execute(
        """SELECT id, serial_number, type_device, status, tanggal, petugas
           FROM reports
           WHERE serial_number LIKE ? OR type_device LIKE ? OR petugas LIKE ?
           ORDER BY id DESC LIMIT 8""",
        (q_like, q_like, q_like)
    ).fetchall()
    conn.close()
    return {"results": [dict(r) for r in rows]}


@app.get("/print")
def print_view(request: Request, ids: str = ""):
    """Tampilan cetak — satu atau banyak laporan sebagai halaman web, tiap laporan
    mulai di halaman baru saat dicetak. Dialog print browser terbuka otomatis."""
    id_list = [int(x) for x in ids.split(",") if x.strip().isdigit()]
    if not id_list:
        return RedirectResponse("/", status_code=303)

    conn = get_conn()
    placeholders = ",".join("?" * len(id_list))
    rows = conn.execute(
        f"SELECT * FROM reports WHERE id IN ({placeholders})", id_list
    ).fetchall()
    by_id = {r["id"]: r for r in rows}
    reports = []
    for rid in id_list:  # pertahankan urutan sesuai pilihan operator
        r = by_id.get(rid)
        if r is None:
            continue
        grouped = photos_for(conn, rid)
        folder = evidence_dir(rid, r["serial_number"]).name
        reports.append({"r": r, "photos": grouped, "folder": folder})
    conn.close()

    if not reports:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(request, "print.html", {"reports": reports})


@app.get("/export")
def export_excel():
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    conn = get_conn()
    rows = conn.execute("SELECT * FROM reports ORDER BY id").fetchall()
    counts = dict(
        conn.execute("SELECT report_id, COUNT(*) FROM photos GROUP BY report_id").fetchall()
    )
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Register Uji Fungsi"
    headers = (
        ["No", "Serial Number", "Type Device", "Lokasi", "Tanggal", "Petugas",
         "Mengetahui 1", "Mengetahui 2", "Mengetahui 3"]
        + [item["nama"] for item in CHECKLIST_ITEMS]
        + ["Status", "Jumlah Foto", "Catatan", "Waktu Input"]
    )
    ws.append(headers)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="D9E2F3")
    for i, r in enumerate(rows, start=1):
        ws.append(
            [i, r["serial_number"], r["type_device"], r["lokasi"], r["tanggal"],
             r["petugas"], r["saksi"], r["saksi2"], r["saksi3"]]
            + [r[f"hasil{j}"] for j in range(1, 7)]
            + [r["status"], counts.get(r["id"], 0), r["catatan"], r["created_at"]]
        )
    for col in ws.columns:
        width = max(len(str(c.value or "")) for c in col) + 2
        ws.column_dimensions[col[0].column_letter].width = min(width, 40)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    fname = f"Register_Uji_Fungsi_{datetime.now():%Y%m%d_%H%M}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@app.get("/settings")
def settings_page(request: Request):
    st = get_settings()
    return templates.TemplateResponse(request, "settings.html", {"settings": st})


@app.post("/api/settings/save")
async def save_settings_endpoint(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    st = save_settings_data(data)
    return {"status": "ok", "message": "Pengaturan berhasil disimpan.", "settings": st}


@app.post("/api/change-pin")
async def change_pin_endpoint(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    old_pin = str(data.get("old_pin", "")).strip()
    new_pin = str(data.get("new_pin", "")).strip()
    if old_pin != supervisor_pin():
        return {"status": "error", "message": "PIN lama salah!"}
    if not new_pin or len(new_pin) < 4:
        return {"status": "error", "message": "PIN baru minimal 4 angka/karakter!"}
    PIN_FILE.write_text(f"{new_pin}\n")
    return {"status": "ok", "message": "PIN Supervisor berhasil diperbarui!"}


def run_backup_in_background():
    """Jalankan pembuatan backup di background thread agar tidak terputus saat user navigasi halaman."""
    global BACKUP_PROGRESS
    if BACKUP_PROGRESS.get("status") == "running":
        return
    t = threading.Thread(target=create_backup_zip, daemon=True)
    t.start()


@app.get("/api/backup/status")
def api_backup_status():
    return BACKUP_PROGRESS


@app.post("/api/backup-now")
def api_backup_now():
    if BACKUP_PROGRESS.get("status") == "running":
        return {
            "status": "running",
            "message": "Proses backup sedang berjalan di latar belakang."
        }
    
    run_backup_in_background()
    return {
        "status": "ok",
        "message": "Proses backup telah dimulai di latar belakang."
    }


@app.get("/api/backup-history")
def api_backup_history():
    BACKUP_BASE_DIR = BASE_DIR / "BACKUP"
    history = []
    if BACKUP_BASE_DIR.exists():
        for item in sorted(BACKUP_BASE_DIR.iterdir(), reverse=True):
            if item.is_dir():
                zips = list(item.glob("*.zip"))
                for z in zips:
                    size_mb = round(z.stat().st_size / (1024 * 1024), 2)
                    history.append({
                        "folder": item.name,
                        "filename": z.name,
                        "size_mb": size_mb if size_mb > 0.01 else "< 0.01",
                        "created_at": item.name.replace("_", " "),
                    })
    return {"status": "ok", "history": history}


@app.get("/backup/download/{folder}/{filename}")
def download_backup_file(folder: str, filename: str):
    safe_folder = "".join(c for c in folder if c.isalnum() or c in "-_")
    safe_file = "".join(c for c in filename if c.isalnum() or c in "-_.")
    path = BASE_DIR / "BACKUP" / safe_folder / safe_file
    if not path.exists() or not path.is_file():
        return RedirectResponse("/settings", status_code=303)
    return FileResponse(path=path, media_type="application/zip", filename=safe_file)


@app.post("/backup/delete/{folder}")
async def delete_backup_folder(folder: str, request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    pin = str(data.get("pin", "")).strip()
    if pin != supervisor_pin():
        return {"status": "error", "message": "PIN Supervisor salah!"}

    safe_folder = "".join(c for c in folder if c.isalnum() or c in "-_")
    target = BASE_DIR / "BACKUP" / safe_folder
    if target.exists() and target.is_dir():
        shutil.rmtree(target, ignore_errors=True)
        return {"status": "ok", "message": "Folder backup berhasil dihapus."}
    return {"status": "error", "message": "Folder backup tidak ditemukan."}


@app.get("/backup")
def backup_data(download: bool = False):
    zip_path, folder_name, zip_filename = create_backup_zip()
    if download:
        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=zip_filename,
        )
    return RedirectResponse("/settings?msg=backup_ok", status_code=303)


