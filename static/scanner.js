/* Scanner barcode via kamera (html5-qrcode). Dipakai di halaman utama & form. */

let _qr = null;

async function openScan(onResult) {
  const modal = document.getElementById("scanmodal");
  const qrContainer = document.getElementById("qrreader");
  if (!modal || !qrContainer) return;

  qrContainer.innerHTML = "";
  modal.hidden = false;

  const isSecure = window.isSecureContext || location.hostname === 'localhost' || location.hostname === '127.0.0.1';
  if (!isSecure && location.protocol !== 'https:') {
    qrContainer.innerHTML = `
      <div style="padding: 24px 16px; text-align: center; color: var(--danger);">
        <i data-lucide="shield-alert" class="icon" style="width: 48px; height: 48px; margin-bottom: 12px;"></i>
        <h4 style="margin: 0 0 8px 0; color: var(--text-main);">Akses Kamera Membutuhkan HTTPS</h4>
        <p style="font-size: 0.88rem; margin: 0; color: var(--text-muted);">
          Browser memblokir kamera pada koneksi HTTP biasa.<br>Silakan buka situs menggunakan <strong>https://</strong>.
        </p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  try {
    if (_qr) {
      try { await _qr.stop(); } catch (e) {}
      _qr = null;
    }
    _qr = new Html5Qrcode("qrreader");
  } catch (e) {
    console.error("Html5Qrcode init error:", e);
  }

  const qrConfig = { fps: 10, qrbox: { width: 280, height: 180 } };
  const onSuccess = (text) => {
    closeScan();
    if (onResult) onResult(text.trim());
  };
  const onError = () => {};

  // Attempt 1: Facing Mode Environment (Rear Camera)
  try {
    await _qr.start({ facingMode: "environment" }, qrConfig, onSuccess, onError);
    return;
  } catch (err1) {
    console.warn("Camera facingMode environment failed, trying fallback...", err1);
  }

  // Attempt 2: Facing Mode User (Front Camera / Laptop Webcam)
  try {
    await _qr.start({ facingMode: "user" }, qrConfig, onSuccess, onError);
    return;
  } catch (err2) {
    console.warn("Camera facingMode user failed, trying camera list...", err2);
  }

  // Attempt 3: Get Cameras List
  try {
    const devices = await Html5Qrcode.getCameras();
    if (devices && devices.length > 0) {
      await _qr.start(devices[0].id, qrConfig, onSuccess, onError);
      return;
    }
  } catch (err3) {
    console.warn("GetCameras failed:", err3);
  }

  // Fallback Error UI
  qrContainer.innerHTML = `
    <div style="padding: 24px 16px; text-align: center; color: var(--danger);">
      <i data-lucide="camera-off" class="icon" style="width: 48px; height: 48px; margin-bottom: 12px; opacity: 0.8;"></i>
      <h4 style="margin: 0 0 8px 0; color: var(--text-main);">Kamera Tidak Dapat Dibuka</h4>
      <p style="font-size: 0.88rem; margin: 0; color: var(--text-muted); line-height: 1.4;">
        Pastikan izin kamera telah diberikan pada browser ini, atau perangkat Anda terhubung dengan kamera.
      </p>
    </div>
  `;
  if (window.lucide) lucide.createIcons();
}

async function closeScan() {
  const modal = document.getElementById("scanmodal");
  if (_qr) {
    try { await _qr.stop(); } catch (e) {}
    try { _qr.clear(); } catch (e) {}
    _qr = null;
  }
  if (modal) modal.hidden = true;
}
