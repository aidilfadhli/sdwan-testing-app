# Project Context: SD-WAN Testing App

**Repository**: `aidilfadhli/sdwan-testing-app`  
**Current Branch**: `raka-adhn`  
**Last Commit**: `Additional Feature: Phase 1 - 3`  
**Status**: All Phase 1, Phase 2, and Phase 3 features fully implemented, verified, committed, and pushed.

---

## 🚀 Executive Summary

The **SD-WAN Mass Testing Web Application** is a specialized tool designed for Telkom Indibiz engineers to conduct rapid, standardized function testing (*Uji Fungsi*) on SD-WAN Edge devices from multiple vendors. 

The system automates barcode scanning, checklist evaluation, evidence photo documentation with watermarks, Berita Acara (BA) Word report compilation, Excel exports, and audit version history.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn (ASGI Web Server).
- **Database**: SQLite (`data/testing.db`) with automatic non-destructive migrations.
- **Document Generation**: `python-docx` (Word `.docx` BA reports), `openpyxl` (4-tab Excel workbooks), `Pillow` (Image thumbnailing & automatic photo watermarking).
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript, HTML5-QRCode scanner, Lucide Icons.
- **Offline Resilience**: `localStorage` + `IndexedDB` auto-draft caching (`static/drafts.js`).

---

## 🏛️ Core System Architecture

### 1. Vendor Registry (`checklist.py`)
Centralized metadata registry for all supported SD-WAN vendors:
- **Fortinet SD-WAN Edge** (Prefixes: `FGT`, `FG`): 6 baseline checklist items, 6 photo sections, template `ba_template_fortinet.docx`.
- **Cisco SD-WAN Edge** (Prefixes: `FGL`, `FOC`): 6 baseline checklist items, 6 photo sections, template `ba_template_cisco.docx`.
- **VMware VeloCloud SD-WAN Edge** (Prefixes: `VC`): 7 baseline checklist items, 6 photo sections, template `ba_template_velocloud.docx`.

### 2. Database Layer (`db.py`)
- Schema manages `reports` and `photos` tables.
- Migration engine automatically adds missing columns (`vendor`, `version`, `parent_report_id`, `hasil7..13`, `ket7..13`) without losing existing data.
- Indexed by `serial_number`, `status`, `vendor`, and `tanggal`.

### 3. Report Engine (`report.py`)
- Compiles official `.docx` Berita Acara documents populated with device identity, checklist results, notes, embedded evidence photos, and signatures.
- **2x2 Grid Signature Table**: Fills individual table cells for:
  - Row 0, Cell 0: **Petugas Penguji**
  - Row 0, Cell 1: **Mengetahui / Saksi 1 (DCS)**
  - Row 1, Cell 0: **Mengetahui / Saksi 2 (DID)**
  - Row 1, Cell 1: **Mengetahui / Saksi 3 (ECS)**

### 4. Web Application Routes (`app.py`)
- `GET /`: Dashboard summary, search filter, statistics cards, and batch actions.
- `GET /scan`: Smart barcode scan handler. Prompts `duplicate_prompt.html` if S/N exists; redirects to `/form` if new S/N.
- `GET /form` & `POST /submit`: New test form submission supporting multi-vendor tabs and re-test versioning.
- `GET /device/{id}`: Detailed inspection report view with multi-version history tree.
- `GET /device/{id}/edit` & `POST /device/{id}/update`: Pre-filled report editing, 1-click photo replacement, photo deletion, and `.docx` auto-regeneration.
- `POST /device/{id}/delete`: Supervisor PIN-protected report deletion.
- `GET /export`: Multi-sheet Excel workbook export (*Ringkasan Semua Vendor*, *Fortinet*, *Cisco*, *VeloCloud*).
- `GET /print`: Web print stylesheet layout for bulk or single printing.
- `GET /api/suggestions`: Autocomplete datalist JSON API.

---

## 📋 Features Implemented (Phase 1 – 3)

### Phase 1: Multi-Vendor Core Engine
- Multi-vendor checklist specification and prefix auto-detection.
- Dynamic vendor `.docx` report generation.
- 2x2 Grid Signature block formatting matching official Telkom layout.
- 4-tab Excel workbook export grouped by vendor.

### Phase 2: Report Editing & Smart Re-inspection Versioning
- **Report Editing (`/edit` & `/update`)**: Full form editability with instant `.docx` regeneration.
- **1-Click Photo Replacement UX**: Dedicated **"Ganti Foto Ini"** button on photo cards with instant client-side preview.
- **Smart Duplicate Scan Prompt (`duplicate_prompt.html`)**: When scanning an existing S/N, offers options for *Re-Test (Version N)*, *Edit Last Report*, or *View History*.
- **Multi-Version Audit Trail**: Re-inspection creates a new record (`version = N`, `parent_report_id = ID`), preserving past test logs intact.

### Phase 3: Offline Draft Resilience, Auto-Suggest & Watermarking
- **Automatic Evidence Photo Watermarking**: Pillow overlays a semi-transparent text banner on saved photos (`S/N: {sn} | {tanggal} | {lokasi}`).
- **Metadata Auto-Suggest API (`/api/suggestions`)**: Dynamically feeds HTML `<datalist>` dropdowns for `lokasi`, `petugas`, `saksi1-3`, and `type_device`.
- **Offline Draft Resilience (`static/drafts.js`)**: Real-time `localStorage` autosave with a yellow restore banner if Wi-Fi drops mid-test.

### Phase 4: Visual Dashboard Analytics & Advanced Filtering
- **Analytics API (`/api/stats`)**: Dedicated backend analytics calculation endpoint in `analytics.py` returning PASS/FAIL ratio, daily throughput trends, top failed checklist items, and model lists.
- **Visual Dashboard Charts (`index.html`)**: Donut chart for PASS/FAIL ratio, bar chart for 14-day daily throughput trends, and visual bar progress ranking for top failed items (via Chart.js).
- **Advanced Filter Chips**: Interactive filter toolbar supporting real-time multi-criteria filtering by Status (PASS/FAIL), Vendor (Fortinet, Cisco, VeloCloud), Date Range (Hari Ini, 7 Hari, 30 Hari), and Device Model.

---

## ⏸️ Deferred Features (On Hold)
Per explicit project direction, the following features are kept on hold for future iterations:
- **Feature 8**: Digital Signature Pad / Canvas drawing.
- **Feature 9**: Delivery Order (DO) Manifest Excel Import.
- **Feature 10**: Direct PDF Export via headless renderer.

---

## 📁 Key File Map

```text
sdwan-testing-app/
├── app.py                      # FastAPI Web Application & Routes
├── checklist.py                # Vendor Specifications & Prefix Auto-Detection
├── db.py                       # SQLite Database Schema & Migrations
├── report.py                   # Word (.docx) Report Compiler & Signature Layout
├── ba_template_fortinet.docx   # Fortinet Word Template
├── ba_template_cisco.docx      # Cisco Word Template
├── ba_template_velocloud.docx  # VeloCloud Word Template
├── static/
│   ├── style.css               # Main CSS Stylesheet
│   ├── scanner.js              # HTML5 Barcode/QR Scanner Script
│   └── drafts.js               # Offline Draft Resilience & Auto-Suggest Script
├── templates/
│   ├── base.html               # Base Template Layout
│   ├── index.html              # Dashboard & Main Table
│   ├── form.html               # Multi-Vendor Inspection Form
│   ├── detail.html             # Inspection Detail & History View
│   ├── edit.html               # Report Edit & Photo Replacement Interface
│   ├── duplicate_prompt.html   # Smart Duplicate Scan Options Prompt
│   ├── print.html              # Web Print Layout
│   └── qr.html                 # Mobile QR Connection Pairing Page
├── data/
│   ├── testing.db              # SQLite Database File
│   └── evidence/               # Photo Evidence Folders per Report
└── context.md                  # Latest Project State & Architecture Reference
```
