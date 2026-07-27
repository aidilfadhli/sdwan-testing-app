import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EVIDENCE_DIR = DATA_DIR / "evidence"
DB_PATH = DATA_DIR / "testing.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_number TEXT NOT NULL,
    vendor TEXT DEFAULT 'fortinet',
    version INTEGER DEFAULT 1,
    parent_report_id INTEGER DEFAULT NULL,
    type_device TEXT DEFAULT '',
    lokasi TEXT DEFAULT '',
    tanggal TEXT DEFAULT '',
    petugas TEXT DEFAULT '',
    saksi TEXT DEFAULT '',
    saksi2 TEXT DEFAULT '',
    saksi3 TEXT DEFAULT '',
    hasil1 TEXT DEFAULT '', ket1 TEXT DEFAULT '',
    hasil2 TEXT DEFAULT '', ket2 TEXT DEFAULT '',
    hasil3 TEXT DEFAULT '', ket3 TEXT DEFAULT '',
    hasil4 TEXT DEFAULT '', ket4 TEXT DEFAULT '',
    hasil5 TEXT DEFAULT '', ket5 TEXT DEFAULT '',
    hasil6 TEXT DEFAULT '', ket6 TEXT DEFAULT '',
    hasil7 TEXT DEFAULT '', ket7 TEXT DEFAULT '',
    hasil8 TEXT DEFAULT '', ket8 TEXT DEFAULT '',
    hasil9 TEXT DEFAULT '', ket9 TEXT DEFAULT '',
    hasil10 TEXT DEFAULT '', ket10 TEXT DEFAULT '',
    hasil11 TEXT DEFAULT '', ket11 TEXT DEFAULT '',
    hasil12 TEXT DEFAULT '', ket12 TEXT DEFAULT '',
    hasil13 TEXT DEFAULT '', ket13 TEXT DEFAULT '',
    catatan TEXT DEFAULT '',
    status TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);
CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL REFERENCES reports(id),
    section TEXT NOT NULL,
    filename TEXT NOT NULL
);
"""


def _migrate(conn: sqlite3.Connection) -> None:
    """Sesuaikan database lama dengan format multi-vendor & re-inspection versi Jul 2026."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(reports)")}
    if "hostname" in cols:
        conn.execute("ALTER TABLE reports RENAME COLUMN hostname TO type_device")
    if "asset_no" in cols:
        conn.execute("ALTER TABLE reports DROP COLUMN asset_no")
    for col in ("saksi2", "saksi3"):
        if col not in cols:
            conn.execute(f"ALTER TABLE reports ADD COLUMN {col} TEXT DEFAULT ''")
    
    if "vendor" not in cols:
        conn.execute("ALTER TABLE reports ADD COLUMN vendor TEXT DEFAULT 'fortinet'")
    if "version" not in cols:
        conn.execute("ALTER TABLE reports ADD COLUMN version INTEGER DEFAULT 1")
    if "parent_report_id" not in cols:
        conn.execute("ALTER TABLE reports ADD COLUMN parent_report_id INTEGER DEFAULT NULL")

    for i in range(7, 14):
        if f"hasil{i}" not in cols:
            conn.execute(f"ALTER TABLE reports ADD COLUMN hasil{i} TEXT DEFAULT ''")
        if f"ket{i}" not in cols:
            conn.execute(f"ALTER TABLE reports ADD COLUMN ket{i} TEXT DEFAULT ''")
            
    conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_sn ON reports(serial_number);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_vendor ON reports(vendor);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_photos_report ON photos(report_id);")
    conn.commit()


def get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    _migrate(conn)
    return conn


def evidence_dir(report_id: int, serial_number: str) -> Path:
    safe_sn = "".join(c for c in serial_number if c.isalnum() or c in "-_") or "NOSN"
    d = EVIDENCE_DIR / f"{safe_sn}_r{report_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d
