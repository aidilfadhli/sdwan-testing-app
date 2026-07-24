"""Generate Berita Acara Uji Fungsi (.docx) dari template dokumen asli (revisi Jul 2026).

Pemetaan tabel pada ba_template.docx:
  tabel 0 : identitas — Type Device, S/N, Lokasi, Tanggal, Petugas (kolom ke-3 diisi nilai)
  tabel 1 : checklist 6 item (kolom Hasil & Keterangan)
  tabel 2-6 : kotak foto (fisik, led, fortios, interface, ping)
  tabel 7 : catatan tambahan
  tabel 8 : tanda tangan — baris 0: Petugas Penguji; baris 1: Mengetahui/Menyetujui (3 nama)
"""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

from checklist import CHECKLIST_ITEMS, PHOTO_SECTIONS

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "ba_template.docx"

GREEN = RGBColor(0x1E, 0x7D, 0x32)
RED = RGBColor(0xC6, 0x28, 0x28)


def _set_cell_text(cell, text, bold=False, color=None, align=None):
    cell.text = ""
    para = cell.paragraphs[0]
    if align is not None:
        para.alignment = align
    run = para.add_run(text or "")
    run.font.size = Pt(10)
    run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def _fill_photos(table, photo_paths):
    cell = table.rows[0].cells[0]
    if not photo_paths:
        _set_cell_text(cell, "( Tidak ada foto )", align=WD_ALIGN_PARAGRAPH.CENTER)
        return
    cell.text = ""
    for i, path in enumerate(photo_paths):
        para = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run()
        try:
            run.add_picture(str(path), width=Inches(4.8))
        except Exception:
            para.add_run(f"( Gagal memuat foto: {Path(path).name} )")


def _replace_para_text(para, text):
    for run in para.runs:
        run.text = ""
    if para.runs:
        para.runs[0].text = text
    else:
        para.add_run(text)


def _fill_signatures(table, petugas, approvers):
    """Nama ditulis di dalam kurung menggantikan garis (____); baris 'Nama / NIP' dihapus
    supaya rapi. Baris 0: petugas; baris 1: tiga nama Mengetahui/Menyetujui."""
    if petugas:
        for para in table.rows[0].cells[0].paragraphs:
            if para.text.strip().startswith("(_"):
                _replace_para_text(para, f"(  {petugas}  )")
            elif "Nama / NIP" in para.text:
                _replace_para_text(para, "")
    if any(approvers):
        parts = [f"(  {n}  )" if n else "(_______________________)" for n in approvers]
        for para in table.rows[1].cells[0].paragraphs:
            if para.text.strip().startswith("(_"):
                _replace_para_text(para, "        ".join(parts))
            elif "Nama / NIP" in para.text:
                _replace_para_text(para, "")


def generate_ba(report: dict, photos_by_section: dict, out_path: Path) -> Path:
    """report: dict baris tabel reports; photos_by_section: {section: [Path, ...]}"""
    doc = Document(TEMPLATE_PATH)

    ident = doc.tables[0]
    values = [
        report.get("type_device", ""),
        report.get("serial_number", ""),
        report.get("lokasi", ""),
        report.get("tanggal", ""),
        report.get("petugas", ""),
    ]
    for row, val in zip(ident.rows, values):
        _set_cell_text(row.cells[2], val, bold=True)

    check = doc.tables[1]
    for i, item in enumerate(CHECKLIST_ITEMS, start=1):
        hasil = report.get(f"hasil{i}", "")
        ket = report.get(f"ket{i}", "")
        color = GREEN if hasil == "OK" else (RED if hasil else None)
        _set_cell_text(check.rows[i].cells[3], hasil, bold=True, color=color,
                       align=WD_ALIGN_PARAGRAPH.CENTER)
        _set_cell_text(check.rows[i].cells[4], ket)

    for offset, section in enumerate(PHOTO_SECTIONS):
        _fill_photos(doc.tables[2 + offset], photos_by_section.get(section["key"], []))

    _set_cell_text(doc.tables[7].rows[0].cells[0], report.get("catatan", ""))

    _fill_signatures(
        doc.tables[8],
        report.get("petugas", ""),
        [report.get("saksi", ""), report.get("saksi2", ""), report.get("saksi3", "")],
    )

    doc.save(out_path)
    return out_path
