"""Module backend analytics untuk SD-WAN Testing App (Phase 4).
Menghitung statistik ringkasan, throughput harian, item yang sering gagal, dan distribusi vendor.
"""

import json
import re
from datetime import datetime, timedelta
from db import get_conn
from checklist import VENDOR_REGISTRY


def get_analytics_data(
    vendor: str | None = None,
    status: str | None = None,
    date_range: str | None = None,
    model: str | None = None,
) -> dict:
    """Mengambil seluruh agregasi data analitik berdasarkan filter query."""
    conn = get_conn()
    try:
        where_clauses = []
        params = []

        if vendor and vendor.strip() and vendor.strip().lower() != "all":
            where_clauses.append("LOWER(vendor) = ?")
            params.append(vendor.strip().lower())

        if status and status.strip() and status.strip().upper() != "ALL":
            where_clauses.append("UPPER(status) = ?")
            params.append(status.strip().upper())

        if model and model.strip() and model.strip().lower() != "all":
            where_clauses.append("type_device = ?")
            params.append(model.strip())

        # Date range filter
        today = datetime.now().date()
        if date_range == "today":
            where_clauses.append("DATE(created_at) = DATE(?)")
            params.append(today.strftime("%Y-%m-%d"))
        elif date_range == "7days":
            start_date = today - timedelta(days=7)
            where_clauses.append("DATE(created_at) >= DATE(?)")
            params.append(start_date.strftime("%Y-%m-%d"))
        elif date_range == "30days":
            start_date = today - timedelta(days=30)
            where_clauses.append("DATE(created_at) >= DATE(?)")
            params.append(start_date.strftime("%Y-%m-%d"))

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # 1. Summary Stats
        stats_query = (
            f"SELECT COUNT(*) AS total, "
            f"SUM(CASE WHEN UPPER(status)='PASS' THEN 1 ELSE 0 END) AS pass_count, "
            f"SUM(CASE WHEN UPPER(status)='FAIL' THEN 1 ELSE 0 END) AS fail_count "
            f"FROM reports{where_sql}"
        )
        row = conn.execute(stats_query, params).fetchone()
        total = row["total"] or 0
        pass_count = row["pass_count"] or 0
        fail_count = row["fail_count"] or 0
        pass_rate = round((pass_count / total * 100), 1) if total > 0 else 0.0

        # 2. Daily Throughput (Last 14 days)
        throughput = get_daily_throughput(conn, where_sql, params)

        # 3. Top Failed Checklist Items
        top_failed = get_top_failed_items(conn, where_sql, params)

        # 4. Vendor Breakdown
        vendor_dist = get_vendor_distribution(conn, where_sql, params)

        # 5. Officer Performance Stats
        officer_stats = get_officer_stats(conn, where_sql, params)

        # 6. Model Defect Stats
        model_stats = get_model_defect_stats(conn, where_sql, params)

        # 7. Component Failure Breakdown (Dynamic Multi-Vendor Category Mapping)
        component_breakdown = get_component_failure_breakdown(conn, where_sql, params)

        # 8. Technician Testing Consistency (with Duration Outlier Clamping)
        technician_consistency = get_technician_consistency(conn, where_sql, params)

        # 9. Daily Shift Progress
        shift_progress = get_daily_shift_progress(conn)

        # 10. Distinct Models for filter dropdown
        model_rows = conn.execute(
            "SELECT DISTINCT type_device FROM reports WHERE type_device IS NOT NULL AND TRIM(type_device) != ''"
        ).fetchall()
        available_models = [m[0].strip() for m in model_rows if m[0] and m[0].strip()]

        return {
            "summary": {
                "total": total,
                "pass": pass_count,
                "fail": fail_count,
                "pass_rate": pass_rate,
            },
            "throughput": throughput,
            "top_failed_items": top_failed,
            "vendor_distribution": vendor_dist,
            "officer_stats": officer_stats,
            "model_stats": model_stats,
            "component_breakdown": component_breakdown,
            "technician_consistency": technician_consistency,
            "shift_progress": shift_progress,
            "available_models": sorted(available_models),
        }
    finally:
        conn.close()


def get_daily_throughput(conn, base_where: str = "", base_params: list = None) -> dict:
    """Agregasi pengujian harian 14 hari terakhir."""
    if base_params is None:
        base_params = []
    
    today = datetime.now().date()
    days_map = {}
    for i in range(13, -1, -1):
        d_obj = today - timedelta(days=i)
        d_str = d_obj.strftime("%Y-%m-%d")
        days_map[d_str] = {
            "date": d_str,
            "label": d_obj.strftime("%d %b"),
            "pass": 0,
            "fail": 0,
            "total": 0,
        }

    query = f"""
        SELECT 
            COALESCE(DATE(created_at), SUBSTR(tanggal, 1, 10)) as test_date,
            SUM(CASE WHEN UPPER(status)='PASS' THEN 1 ELSE 0 END) as pass_c,
            SUM(CASE WHEN UPPER(status)='FAIL' THEN 1 ELSE 0 END) as fail_c,
            COUNT(*) as total_c
        FROM reports
        {base_where}
        GROUP BY test_date
        ORDER BY test_date DESC
        LIMIT 30
    """
    rows = conn.execute(query, base_params).fetchall()
    for r in rows:
        d = r["test_date"]
        if d in days_map:
            days_map[d]["pass"] = r["pass_c"] or 0
            days_map[d]["fail"] = r["fail_c"] or 0
            days_map[d]["total"] = r["total_c"] or 0

    dates_list = list(days_map.values())
    return {
        "labels": [d["label"] for d in dates_list],
        "dates": [d["date"] for d in dates_list],
        "pass_data": [d["pass"] for d in dates_list],
        "fail_data": [d["fail"] for d in dates_list],
        "total_data": [d["total"] for d in dates_list],
    }


def get_top_failed_items(conn, base_where: str = "", base_params: list = None) -> list[dict]:
    """Parse checklist_json pada laporan status FAIL untuk menemukan item yang sering gagal."""
    if base_params is None:
        base_params = []

    where_clause = base_where
    params = list(base_params)
    if "WHERE" in where_clause:
        where_clause += " AND UPPER(status) = 'FAIL'"
    else:
        where_clause = " WHERE UPPER(status) = 'FAIL'"

    cols = {r[1] for r in conn.execute("PRAGMA table_info(reports)")}
    select_cols = ["vendor", "hasil1", "hasil2", "hasil3", "hasil4", "hasil5", "hasil6", "hasil7"]
    if "checklist_json" in cols:
        select_cols.append("checklist_json")

    query = f"SELECT {', '.join(select_cols)} FROM reports {where_clause}"
    rows = conn.execute(query, params).fetchall()

    fail_counter = {}

    for r in rows:
        v_id = r["vendor"] if ("vendor" in r.keys() and r["vendor"]) else "fortinet"
        v_spec = VENDOR_REGISTRY.get(v_id, VENDOR_REGISTRY["fortinet"])
        items_spec = {item["key"]: item["nama"] for item in v_spec.get("items", [])}

        c_json = r["checklist_json"] if ("checklist_json" in r.keys() and r["checklist_json"]) else None
        found_in_json = False
        if c_json:
            try:
                c_data = json.loads(c_json)
                for key, val in c_data.items():
                    if isinstance(val, dict) and val.get("hasil") == "NOT OK":
                        item_name = items_spec.get(key, key)
                        fail_counter[item_name] = fail_counter.get(item_name, 0) + 1
                        found_in_json = True
            except Exception:
                pass

        if not found_in_json:
            for idx, item in enumerate(v_spec.get("items", []), start=1):
                col_name = f"hasil{idx}"
                if col_name in r.keys() and r[col_name] == "NOT OK":
                    item_name = item["nama"]
                    fail_counter[item_name] = fail_counter.get(item_name, 0) + 1

    result = [{"name": name, "count": count} for name, count in fail_counter.items()]
    result.sort(key=lambda x: x["count"], reverse=True)
    return result[:5]


def get_vendor_distribution(conn, base_where: str = "", base_params: list = None) -> list[dict]:
    """Menghitung distribusi jumlah pengujian per vendor."""
    if base_params is None:
        base_params = []
    query = f"SELECT vendor, COUNT(*) as count FROM reports {base_where} GROUP BY vendor"
    rows = conn.execute(query, base_params).fetchall()

    vendor_map = {}
    for r in rows:
        v_id = (r["vendor"] or "fortinet").lower()
        v_name = VENDOR_REGISTRY.get(v_id, {}).get("name", v_id.capitalize())
        vendor_map[v_name] = r["count"]

    return [{"vendor": name, "count": count} for name, count in vendor_map.items()]


def get_officer_stats(conn, base_where: str = "", base_params: list = None) -> list[dict]:
    """Menghitung total pengujian, lulus, gagal, dan pass rate per petugas."""
    if base_params is None:
        base_params = []
    
    where_clause = base_where
    if "WHERE" in where_clause:
        where_clause += " AND petugas IS NOT NULL AND TRIM(petugas) != ''"
    else:
        where_clause = " WHERE petugas IS NOT NULL AND TRIM(petugas) != ''"

    query = f"""
        SELECT 
            petugas,
            COUNT(*) as total,
            SUM(CASE WHEN UPPER(status)='PASS' THEN 1 ELSE 0 END) as pass_c,
            SUM(CASE WHEN UPPER(status)='FAIL' THEN 1 ELSE 0 END) as fail_c
        FROM reports
        {where_clause}
        GROUP BY petugas
        ORDER BY total DESC
        LIMIT 10
    """
    rows = conn.execute(query, base_params).fetchall()
    res = []
    for r in rows:
        tot = r["total"] or 0
        p_c = r["pass_c"] or 0
        rate = round((p_c / tot * 100), 1) if tot > 0 else 0.0
        res.append({
            "officer": r["petugas"],
            "total": tot,
            "pass": p_c,
            "fail": r["fail_c"] or 0,
            "pass_rate": rate
        })
    return res


def get_model_defect_stats(conn, base_where: str = "", base_params: list = None) -> list[dict]:
    """Menghitung statistik tingkat kegagalan (defect rate) per tipe model perangkat."""
    if base_params is None:
        base_params = []

    where_clause = base_where
    if "WHERE" in where_clause:
        where_clause += " AND type_device IS NOT NULL AND TRIM(type_device) != ''"
    else:
        where_clause = " WHERE type_device IS NOT NULL AND TRIM(type_device) != ''"

    query = f"""
        SELECT 
            type_device,
            COUNT(*) as total,
            SUM(CASE WHEN UPPER(status)='PASS' THEN 1 ELSE 0 END) as pass_c,
            SUM(CASE WHEN UPPER(status)='FAIL' THEN 1 ELSE 0 END) as fail_c
        FROM reports
        {where_clause}
        GROUP BY type_device
        ORDER BY total DESC
        LIMIT 10
    """
    rows = conn.execute(query, base_params).fetchall()
    res = []
    for r in rows:
        tot = r["total"] or 0
        f_c = r["fail_c"] or 0
        rate = round((f_c / tot * 100), 1) if tot > 0 else 0.0
        res.append({
            "model": r["type_device"],
            "total": tot,
            "pass": r["pass_c"] or 0,
            "fail": f_c,
            "fail_rate": rate
        })
    return res


def get_component_failure_breakdown(conn, base_where: str = "", base_params: list = None) -> list[dict]:
    """Kategorisasi kegagalan komponen hardware (Physical & Power, Interface & SFP, Firmware, Documentation)."""
    if base_params is None:
        base_params = []

    where_clause = base_where
    if "WHERE" in where_clause:
        where_clause += " AND UPPER(status) = 'FAIL'"
    else:
        where_clause = " WHERE UPPER(status) = 'FAIL'"

    cols = {r[1] for r in conn.execute("PRAGMA table_info(reports)")}
    select_cols = ["vendor", "hasil1", "hasil2", "hasil3", "hasil4", "hasil5", "hasil6", "hasil7"]
    if "checklist_json" in cols:
        select_cols.append("checklist_json")

    query = f"SELECT {', '.join(select_cols)} FROM reports {where_clause}"
    rows = conn.execute(query, base_params).fetchall()

    category_counts = {}

    for r in rows:
        v_id = (r["vendor"] if ("vendor" in r.keys() and r["vendor"]) else "fortinet").lower()
        v_spec = VENDOR_REGISTRY.get(v_id, VENDOR_REGISTRY["fortinet"])
        items_spec = v_spec.get("items", [])

        # Process checklist items
        for idx, item in enumerate(items_spec, start=1):
            col_name = f"hasil{idx}"
            if col_name in r.keys() and r[col_name] == "NOT OK":
                cat = item.get("category", "General")
                category_counts[cat] = category_counts.get(cat, 0) + 1

    total_failures = sum(category_counts.values())
    result = []
    for cat_name, count in category_counts.items():
        pct = round((count / total_failures * 100), 1) if total_failures > 0 else 0.0
        result.append({"category": cat_name, "count": count, "percentage": pct})

    result.sort(key=lambda x: x["count"], reverse=True)
    return result


def get_technician_consistency(conn, base_where: str = "", base_params: list = None) -> list[dict]:
    """Hitung statistik performa dan rata-rata durasi inspeksi per petugas (dengan clamping outlier > 30 menit)."""
    if base_params is None:
        base_params = []

    where_clause = base_where
    if "WHERE" in where_clause:
        where_clause += " AND petugas IS NOT NULL AND TRIM(petugas) != ''"
    else:
        where_clause = " WHERE petugas IS NOT NULL AND TRIM(petugas) != ''"

    query = f"""
        SELECT 
            petugas,
            COUNT(*) as total,
            SUM(CASE WHEN UPPER(status)='PASS' THEN 1 ELSE 0 END) as pass_c,
            SUM(CASE WHEN UPPER(status)='FAIL' THEN 1 ELSE 0 END) as fail_c,
            AVG(CASE WHEN duration_seconds > 0 AND duration_seconds <= 1800 THEN duration_seconds ELSE NULL END) as avg_duration
        FROM reports
        {where_clause}
        GROUP BY petugas
        ORDER BY total DESC
        LIMIT 10
    """
    rows = conn.execute(query, base_params).fetchall()
    res = []
    for r in rows:
        tot = r["total"] or 0
        p_c = r["pass_c"] or 0
        rate = round((p_c / tot * 100), 1) if tot > 0 else 0.0
        avg_dur_sec = r["avg_duration"] or 0
        avg_dur_min = round(avg_dur_sec / 60, 1) if avg_dur_sec > 0 else 0.0

        res.append({
            "officer": r["petugas"],
            "total": tot,
            "pass": p_c,
            "fail": r["fail_c"] or 0,
            "pass_rate": rate,
            "avg_duration_minutes": avg_dur_min
        })
    return res


def get_daily_shift_progress(conn, target_quota: int = 30) -> dict:
    """Hitung progress shift hari ini, kecepatan (unit/jam), dan split PASS/FAIL."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    query = """
        SELECT 
            COUNT(*) as today_total,
            SUM(CASE WHEN UPPER(status)='PASS' THEN 1 ELSE 0 END) as today_pass,
            SUM(CASE WHEN UPPER(status)='FAIL' THEN 1 ELSE 0 END) as today_fail
        FROM reports
        WHERE DATE(created_at) = DATE(?)
    """
    row = conn.execute(query, [today_str]).fetchone()
    tot = row["today_total"] if row and row["today_total"] else 0
    p_c = row["today_pass"] if row and row["today_pass"] else 0
    f_c = row["today_fail"] if row and row["today_fail"] else 0

    progress_pct = min(100.0, round((tot / target_quota * 100), 1)) if target_quota > 0 else 0.0
    
    # Calculate velocity based on current hour of day
    current_hour = max(1, datetime.now().hour - 7) # assuming shift starts ~08:00 AM
    velocity = round(tot / current_hour, 1)

    return {
        "today_total": tot,
        "today_pass": p_c,
        "today_fail": f_c,
        "target_quota": target_quota,
        "progress_percentage": progress_pct,
        "units_per_hour": velocity,
    }


def get_device_health_history(serial_number: str) -> dict:
    """Ambil seluruh riwayat pengujian untuk satu Serial Number (S/N). Sanitasi input S/N & urutkan dari yang terbaru."""
    if not serial_number:
        return {
            "serial_number": "",
            "total_attempts": 0,
            "has_history": False,
            "is_chronic_defect": False,
            "pass_count": 0,
            "fail_count": 0,
            "latest_status": "",
            "history": []
        }

    sn_clean = re.sub(r"[\r\n\t\s]", "", serial_number).upper()
    conn = get_conn()
    try:
        query = """
            SELECT * FROM reports 
            WHERE REPLACE(REPLACE(REPLACE(REPLACE(UPPER(serial_number), CHAR(13), ''), CHAR(10), ''), CHAR(9), ''), ' ', '') = ?
            ORDER BY version DESC, id DESC
        """
        rows = conn.execute(query, [sn_clean]).fetchall()
        
        if not rows:
            return {
                "serial_number": sn_clean,
                "total_attempts": 0,
                "has_history": False,
                "is_chronic_defect": False,
                "pass_count": 0,
                "fail_count": 0,
                "latest_status": "",
                "history": []
            }

        total_attempts = len(rows)
        pass_count = sum(1 for r in rows if (r["status"] or "").upper() == "PASS")
        fail_count = sum(1 for r in rows if (r["status"] or "").upper() == "FAIL")
        latest_status = (rows[0]["status"] or "").upper()
        is_chronic = fail_count >= 2

        history_records = []
        for r in rows:
            v_id = (r["vendor"] or "fortinet").lower()
            v_spec = VENDOR_REGISTRY.get(v_id, VENDOR_REGISTRY["fortinet"])
            items_spec = v_spec.get("items", [])

            failed_items = []
            for idx, item in enumerate(items_spec, start=1):
                col_h = f"hasil{idx}"
                col_k = f"ket{idx}"
                if col_h in r.keys() and r[col_h] == "NOT OK":
                    failed_items.append({
                        "key": item["key"],
                        "name": item["nama"],
                        "category": item.get("category", "General"),
                        "note": r[col_k] if col_k in r.keys() else ""
                    })

            history_records.append({
                "id": r["id"],
                "version": r["version"],
                "status": (r["status"] or "").upper(),
                "created_at": r["created_at"],
                "vendor": v_id,
                "vendor_name": v_spec.get("name", v_id),
                "type_device": r["type_device"] or "",
                "petugas": r["petugas"] or "",
                "catatan": r["catatan"] or "",
                "failed_items": failed_items,
                "duration_seconds": r["duration_seconds"] if "duration_seconds" in r.keys() else 0
            })

        return {
            "serial_number": sn_clean,
            "total_attempts": total_attempts,
            "has_history": True,
            "is_chronic_defect": is_chronic,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "latest_status": latest_status,
            "history": history_records
        }
    finally:
        conn.close()

