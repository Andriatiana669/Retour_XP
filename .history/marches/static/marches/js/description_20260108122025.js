/* Copie + bascule Grand/Petit + mémorisation préférence */
document.addEventListener('DOMContentLoaded', () => {
  // --- copie dans le presse-papiers ---
  document.querySelectorAll('.btn-copy').forEach(btn => {
    btn.addEventListener('click', async () => {
      const text = btn.dataset.contenu;
      try {
        await navigator.clipboard.writeText(text);
        btn.innerHTML = '<i class="fas fa-check"></i>';
        setTimeout(() => btn.innerHTML = '<i class="far fa-copy"></i>', 1200);
      } catch (err) {
        console.error('Copie échouée', err);
      }
    });
  });

  // --- bascule Grand / Petit ---
  const btnGrand = document.getElementById('btnGrand');
  const btnPetit = document.getElementById('btnPetit');
  const container = document.getElementById('cartesContainer');

  function setVue(grand) {
    container.classList.toggle('compact', !grand);
    btnGrand.classList.toggle('active', grand);
    btnPetit.classList.toggle('active', !grand);
    localStorage.setItem('carteVueGrand', grand);
  }

  btnGrand.addEventListener('click', () => setVue(true));
  btnPetit.addEventListener('click', () => setVue(false));

  // restaure la préférence utilisateur
  setVue(localStorage.getItem('carteVueGrand') !== 'false');
});