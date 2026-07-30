# Implementation Plan - Advanced Analytics (Individual-Device Focused)

Refine and extend the existing analytics dashboard to specifically optimize for **individual unit testing workflows**. Instead of bulk batch metrics, this plan focuses on **Individual Device Health Cards**, **Component-Level Defect Analysis**, **Technician Testing Consistency**, and **Live Daily Shift Progress**.

## User Review Required

> [!IMPORTANT]
> **Key Architectural Choices & Technical Refinements (10/10 Precision)**:
> 1. **Dynamic Multi-Vendor Component Mapping**: `VENDOR_REGISTRY` in `checklist.py` is enriched with a `category` attribute per item (e.g. *Physical & Power*, *Interface & SFP*, *Firmware & System*, *Documentation & Model*) to accurately categorize defects across Fortinet, Cisco, and VeloCloud.
> 2. **Device Health Warning Banner & Rich History Payload**: Automatically displays a warning badge on the inspection form when a technician scans a serial number (S/N) that has failed previously or has been re-tested multiple times. The `/api/device-history/<SN>` endpoint returns detailed past failure items, `catatan`, and version timeline.
> 3. **Active Timer Accumulation & Outlier Protection**: Tracks `active_seconds` in `drafts.js`/`analytics.js` (pausing when tab is hidden or closed). Backend metrics clamp durations to max 1800s (30 mins) to prevent idle tab open time from distorting technician speed averages.
> 4. **Strict S/N Sanitization**: Enforces `serial_number.replace(/[\r\n\t\s]/g, '').toUpperCase()` and SQL `TRIM(UPPER(serial_number))` matching to eliminate barcode scanner control character and whitespace discrepancies.

## Proposed Changes

### Data & Vendor Registry Layer

#### [MODIFY] [checklist.py](file:///c:/Users/Raka/Documents/COOLYEAHH/KaPe/sdwan-testing-app/checklist.py)
- Enrich all items in `VENDOR_REGISTRY` (`fortinet`, `cisco`, `velocloud`) with a standardized `category` attribute:
  - `Physical & Power`: Casing, power-on test, physical ports.
  - `Interface & SFP`: LAN interfaces, WAN, SFP modules, ping connectivity.
  - `Firmware & System`: FortiOS/Cisco/VeloCloud firmware version check.
  - `Documentation & Model`: Model verification, PO check, S/N verification.

#### [MODIFY] [db.py](file:///c:/Users/Raka/Documents/COOLYEAHH/KaPe/sdwan-testing-app/db.py)
- Update `_migrate()` engine to add `duration_seconds INTEGER DEFAULT 0` column to `reports` table if not present.

---

### Backend Analytics Engine & APIs

#### [MODIFY] [analytics.py](file:///c:/Users/Raka/Documents/COOLYEAHH/KaPe/sdwan-testing-app/analytics.py)
- **`get_device_health_history(serial_number)`**:
  - Sanitize and normalize S/N query using `TRIM(UPPER(serial_number))`.
  - Fetch all prior test records for the S/N ordered by `version DESC`.
  - Return attempts count, pass/fail ratio, chronic defect flag ($\ge 2$ past failures), and structured list of past failed items (`item_name`, `category`, `ket`, `catatan`).
- **`get_component_failure_breakdown(where_sql, params)`**:
  - Dynamically look up `vendor` and failed item keys (`hasil1`..`hasil13`) against `VENDOR_REGISTRY` categories.
  - Aggregate failure counts accurately per category across multi-vendor records.
- **`get_technician_consistency(where_sql, params)`**:
  - Calculate total units tested, pass/fail %, and average inspection duration per technician.
  - Apply idle time guard (filter out or clamp `duration_seconds > 1800` seconds).
- **`get_daily_shift_progress(petugas=None, target_quota=30)`**:
  - Calculate today's testing count, PASS/FAIL split, testing velocity (units/hour), and shift quota progress %.

#### [MODIFY] [app.py](file:///c:/Users/Raka/Documents/COOLYEAHH/KaPe/sdwan-testing-app/app.py)
- **`GET /api/device-history/<serial_number>`**: API endpoint returning full JSON health card and historical defect timeline for S/N scan popups.
- Update `GET /analytics` and `GET /api/stats` routes to incorporate component failure breakdown, technician performance, and shift progress metrics.

---

### Frontend UI & Client Scripts

#### [MODIFY] [static/analytics.js](file:///c:/Users/Raka/Documents/COOLYEAHH/KaPe/sdwan-testing-app/static/analytics.js) & [static/drafts.js](file:///c:/Users/Raka/Documents/COOLYEAHH/KaPe/sdwan-testing-app/static/drafts.js)
- Implement **Active Timer Accumulator**:
  - Track active time `active_seconds`; pause counter when `document.visibilityState === 'hidden'`.
  - Store `active_seconds` inside IndexedDB / localStorage drafts so resuming a draft preserves exact working time.
- Sanitize scanner inputs using `.replace(/[\r\n\t\s]/g, '').toUpperCase()`.
- Fetch and render device health card dynamically upon scanning an S/N barcode.

#### [MODIFY] [templates/analytics.html](file:///c:/Users/Raka/Documents/COOLYEAHH/KaPe/sdwan-testing-app/templates/analytics.html)
- Add **Component Failure Breakdown** card with proportional bar visualizer.
- Add **Technician Consistency Table** comparing test volume, pass rate %, and avg inspection time.

#### [MODIFY] [templates/form.html](file:///c:/Users/Raka/Documents/COOLYEAHH/KaPe/sdwan-testing-app/templates/form.html) & [templates/index.html](file:///c:/Users/Raka/Documents/COOLYEAHH/KaPe/sdwan-testing-app/templates/index.html)
- Add **Device Health Warning Banner** on inspection form when scanning an S/N with past failures.
- Add **Live Daily Shift Pace Widget** on dashboard header showing today's target progress (e.g. `22 / 30 Units`).

---

## Verification Plan

### Automated Tests
- Run full Python unit test suite:
  ```powershell
  .\.venv\Scripts\python.exe -m unittest discover tests
  ```
- Add comprehensive API contract tests in `tests/test_analytics.py`:
  - Unit tests for `get_device_health_history()` with multi-vendor test fixtures.
  - Tests for `get_component_failure_breakdown()` validating dynamic vendor category aggregation.
  - Tests for `get_technician_consistency()` verifying duration outlier clamping.
  - API endpoint response schema tests for `/api/device-history/<serial_number>`.

### Manual Verification
1. **Device Health Popup & Control Characters**: Scan an S/N barcode (including barcodes with trailing carriage returns) and verify sanitized lookup displays past defect notes and version timeline.
2. **Draft Resume Timer**: Save a draft form, minimize/hide the tab for 1 minute, resume draft, and verify `active_seconds` only counts active interaction time.
3. **Multi-Vendor Component Breakdown**: Submit test reports with failures for Fortinet, Cisco, and VeloCloud, verifying categories aggregate accurately.
