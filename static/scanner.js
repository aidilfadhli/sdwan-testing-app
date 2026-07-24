/* Scanner barcode via kamera (html5-qrcode). Dipakai di halaman utama & form. */

/* Hapus laporan: minta PIN supervisor, diverifikasi di server. */
function askPin(form) {
  const p = prompt("Masukkan PIN supervisor untuk menghapus laporan ini:");
  if (!p) return false;
  form.pin.value = p;
  return true;
}
let _qr = null;

async function openScan(onResult) {
  if (!window.isSecureContext) {
    alert("Kamera hanya bisa diakses lewat alamat HTTPS.\nBuka aplikasi lewat alamat https:// yang tertera di halaman utama / QR.");
    return;
  }
  const modal = document.getElementById("scanmodal");
  modal.hidden = false;
  _qr = new Html5Qrcode("qrreader");
  try {
    await _qr.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: { width: 300, height: 160 } },
      (text) => { closeScan(); onResult(text.trim()); },
      () => {}
    );
  } catch (err) {
    closeScan();
    alert("Tidak bisa membuka kamera: " + err +
      "\nPastikan izin kamera diberikan untuk situs ini.");
  }
}

async function closeScan() {
  const modal = document.getElementById("scanmodal");
  if (_qr) {
    try { await _qr.stop(); _qr.clear(); } catch (e) {}
    _qr = null;
  }
  modal.hidden = true;
}
