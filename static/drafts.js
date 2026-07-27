/* static/drafts.js - Offline Form Draft Resilience & Auto-Suggest Integration */

document.addEventListener('DOMContentLoaded', () => {
  initAutoSuggestions();
  initFormDraftResilience();
});

/* 1. Auto-Suggest Datalist Integration */
async function initAutoSuggestions() {
  try {
    const res = await fetch('/api/suggestions');
    if (!res.ok) return;
    const data = await res.json();
    
    // Bind datalists to fields
    bindDatalist('lokasi', data.lokasi || []);
    bindDatalist('petugas', data.petugas || []);
    bindDatalist('saksi', data.saksi || []);
    bindDatalist('saksi2', data.saksi2 || []);
    bindDatalist('saksi3', data.saksi3 || []);
    bindDatalist('type_device', data.type_device || []);
  } catch (err) {
    console.log('Suggestions offline or error:', err);
  }
}

function bindDatalist(inputId, values) {
  const input = document.getElementById(inputId);
  if (!input || !values.length) return;
  
  const listId = 'dl_' + inputId;
  let datalist = document.getElementById(listId);
  if (!datalist) {
    datalist = document.createElement('datalist');
    datalist.id = listId;
    document.body.appendChild(datalist);
  }
  datalist.innerHTML = '';
  values.forEach(val => {
    const opt = document.createElement('option');
    opt.value = val;
    datalist.appendChild(opt);
  });
  input.setAttribute('list', listId);
}

/* 2. Offline Form Draft Resilience */
function initFormDraftResilience() {
  const form = document.getElementById('testform') || document.getElementById('editform');
  if (!form) return;
  
  const snField = document.getElementById('snfield');
  const draftKey = 'sdwan_draft_' + (snField ? snField.value.trim() : 'general');

  // Check if saved draft exists
  const savedDraftStr = localStorage.getItem(draftKey);
  if (savedDraftStr) {
    try {
      const draft = JSON.parse(savedDraftStr);
      showRestoreBanner(form, draft, draftKey);
    } catch (e) {
      localStorage.removeItem(draftKey);
    }
  }

  // Auto-save form changes continuously
  form.addEventListener('input', () => debounceAutoSave(form, draftKey));
  form.addEventListener('change', () => debounceAutoSave(form, draftKey));

  // Clear draft on submit
  form.addEventListener('submit', () => {
    localStorage.removeItem(draftKey);
  });
}

let saveTimer;
function debounceAutoSave(form, draftKey) {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => saveFormState(form, draftKey), 600);
}

function saveFormState(form, draftKey) {
  const formData = new FormData(form);
  const draft = {};
  for (let [key, val] of formData.entries()) {
    if (typeof val === 'string' && key !== 'delete_photo_ids') {
      draft[key] = val;
    }
  }
  draft._timestamp = new Date().toISOString();
  localStorage.setItem(draftKey, JSON.stringify(draft));
  showSaveIndicator();
}

function showSaveIndicator() {
  let ind = document.getElementById('draft-indicator');
  if (!ind) {
    ind = document.createElement('div');
    ind.id = 'draft-indicator';
    ind.style.cssText = 'position:fixed; bottom:16px; right:16px; background:rgba(20,49,92,0.85); color:#fff; font-size:0.78rem; padding:6px 12px; border-radius:20px; z-index:9999; pointer-events:none; transition:opacity 0.4s;';
    document.body.appendChild(ind);
  }
  ind.textContent = '💾 Draft Tersimpan Otomatis';
  ind.style.opacity = '1';
  setTimeout(() => { ind.style.opacity = '0'; }, 1800);
}

function showRestoreBanner(form, draft, draftKey) {
  const banner = document.createElement('div');
  banner.className = 'infobanner';
  banner.style.cssText = 'background:#fff3cd; color:#856404; padding:12px 16px; border-radius:8px; margin-bottom:20px; border-left:4px solid #ffebaa; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; font-size:0.9rem;';
  
  const timeStr = draft._timestamp ? new Date(draft._timestamp).toLocaleTimeString() : '';
  banner.innerHTML = `
    <div>
      <strong>📥 Ditemukan Draft Pengujian Belum Selesai (${timeStr})</strong>
      <div style="font-size:0.8rem; opacity:0.9;">Apakah Anda ingin memulihkan isian radio & catatan terakhir?</div>
    </div>
    <div style="display:flex; gap:8px;">
      <button type="button" class="btn small primary" id="btn-restore-draft">Pulihkan Draft</button>
      <button type="button" class="btn small secondary" id="btn-discard-draft" style="background:#fff;">Abaikan</button>
    </div>
  `;

  form.parentNode.insertBefore(banner, form);

  document.getElementById('btn-restore-draft').onclick = () => {
    restoreFormState(form, draft);
    banner.remove();
  };
  document.getElementById('btn-discard-draft').onclick = () => {
    localStorage.removeItem(draftKey);
    banner.remove();
  };
}

function restoreFormState(form, draft) {
  Object.keys(draft).forEach(key => {
    if (key.startsWith('_')) return;
    const val = draft[key];
    const inputs = form.querySelectorAll(`[name="${key}"]`);
    inputs.forEach(input => {
      if (input.type === 'radio') {
        if (input.value === val) input.checked = true;
      } else if (input.type !== 'file') {
        input.value = val;
      }
    });
  });
  alert('Draft pengujian berhasil dipulihkan!');
}
