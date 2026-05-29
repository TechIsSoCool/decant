const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const spinnerOverlay = document.getElementById('spinnerOverlay');
const toastContainer = document.getElementById('toastContainer');

const SUPPORTED_EXTENSIONS = new Set(['.docx', '.pdf']);

function getExtension(filename) {
  const idx = filename.lastIndexOf('.');
  return idx >= 0 ? filename.slice(idx).toLowerCase() : '';
}

function showToast(message, type = 'error', durationMs = 5000) {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s ease';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, durationMs);
}

function triggerDownload(markdown, filename) {
  const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

async function processFile(file) {
  const ext = getExtension(file.name);
  if (!SUPPORTED_EXTENSIONS.has(ext)) {
    showToast('Only .docx and .pdf files are supported.', 'error');
    return;
  }

  spinnerOverlay.classList.add('visible');
  spinnerOverlay.removeAttribute('aria-hidden');

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/convert', { method: 'POST', body: formData });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      if (data.detail === 'unsupported_type') {
        showToast('Only .docx and .pdf files are supported.', 'error');
      } else {
        showToast('Conversion failed. Please try again.', 'error');
      }
      return;
    }

    const data = await response.json();
    triggerDownload(data.markdown, data.filename);

    if (data.warning === 'scanned_pdf') {
      showToast('PDF appears to contain scanned images — extracted text may be limited.', 'warning', 7000);
    } else {
      showToast(`Downloaded ${data.filename}`, 'success', 3000);
    }
  } catch (err) {
    showToast('An unexpected error occurred. Please try again.', 'error');
  } finally {
    spinnerOverlay.classList.remove('visible');
    spinnerOverlay.setAttribute('aria-hidden', 'true');
    fileInput.value = '';
  }
}

// Drag-and-drop
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', (e) => {
  if (!dropZone.contains(e.relatedTarget)) {
    dropZone.classList.remove('drag-over');
  }
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) processFile(file);
});

// Click-to-browse (the hidden input covers the zone via position:absolute)
fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (file) processFile(file);
});

// Keyboard accessibility
dropZone.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    fileInput.click();
  }
});
