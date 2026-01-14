document.addEventListener('DOMContentLoaded', () => {
  // Auto-hauteur textarea
  const tx = document.querySelector('textarea');
  if (tx) {
    tx.setAttribute('rows', 1);
    tx.addEventListener('input', () => {
      tx.style.height = 'auto';
      tx.style.height = tx.scrollHeight + 'px';
    });
  }

  // Aperçu image avant envoi
  const fileInp = document.querySelector('input[type="file"]');
  const preview = document.createElement('img');
  preview.style.maxWidth = '180px';
  preview.style.marginTop = '.75rem';
  preview.style.borderRadius = '.375rem';
  fileInp?.addEventListener('change', () => {
    const [file] = fileInp.files;
    if (file) {
      preview.src = URL.createObjectURL(file);
      fileInp.parentElement.appendChild(preview);
    }
  });
});