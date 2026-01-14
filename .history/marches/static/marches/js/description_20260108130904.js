/* Copie + bascule Grand/Petit + tri + filtre + mémorisation préférence */
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
  setVue(localStorage.getItem('carteVueGrand') !== 'false');

  // --- TRI + FILTRE ---
  const searchInp = document.getElementById('searchCarte');
  const dateInp = document.getElementById('filterDate');
  const sortSel = document.getElementById('sortSelect');
  const cartes = Array.from(document.querySelectorAll('.carte'));

  function applyFilters() {
    const search = searchInp.value.trim().toLowerCase();
    const dateVal = dateInp.value;
    const sort = sortSel.value;

    // tri
    const sorter = {
      'date-desc': (a, b) => new Date(b.dataset.date) - new Date(a.dataset.date),
      'date-asc': (a, b) => new Date(a.dataset.date) - new Date(b.dataset.date),
      'titre-az': (a, b) => a.dataset.titre.localeCompare(b.dataset.titre),
      'titre-za': (a, b) => b.dataset.titre.localeCompare(a.dataset.titre)
    };
    cartes.sort(sorter[sort] || sorter['date-desc']);

    // filtre + affichage
    cartes.forEach(c => {
      const textMatch = !search || c.dataset.titre.includes(search);
      const dateMatch = !dateVal || c.dataset.date === dateVal;
      c.style.display = (textMatch && dateMatch) ? '' : 'none';
    });

    // ré-insère dans l'ordre
    cartes.forEach(c => container.appendChild(c));
  }
  [searchInp, dateInp, sortSel].forEach(el => el.addEventListener('input', applyFilters));
  applyFilters(); // initial
});