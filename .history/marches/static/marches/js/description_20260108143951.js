/* Copie + bascule Grand/Petit + tri + filtre + mémorisation préférence */
document.addEventListener('DOMContentLoaded', () => {
  // --- Copie dans le presse-papiers ---
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

  // --- Bascule Grand / Petit ---
  const btnGrand = document.getElementById('btnGrand');
  const btnPetit = document.getElementById('btnPetit');
  const container = document.getElementById('cartesContainer');

  function setVue(grand) {
    container.classList.toggle('compact', !grand);
    btnGrand.classList.toggle('active', grand);
    btnPetit.classList.toggle('active', !grand);
    localStorage.setItem('carteVueGrand', grand);
  }

  if (btnGrand && btnPetit && container) {
    btnGrand.addEventListener('click', () => setVue(true));
    btnPetit.addEventListener('click', () => setVue(false));
    setVue(localStorage.getItem('carteVueGrand') !== 'false');
  }

  // --- TRI + FILTRE ---
  const searchFieldSel = document.getElementById('searchField');
  const searchInp = document.getElementById('searchCarte');
  const dateInp = document.getElementById('filterDate'); // Non utilisé dans ton HTML actuel
  const sortSel = document.getElementById('sortSelect');
  const cartes = Array.from(document.querySelectorAll('.carte'));

  function applyFilters() {
    if (!searchFieldSel || !searchInp || !sortSel || !container) {
      console.warn("Un ou plusieurs éléments de filtre/tri sont introuvables.");
      return;
    }

    const field = searchFieldSel.value;
    const search = searchInp.value.trim().toLowerCase();
    const sort = sortSel.value;

    // Tri
    const sorter = {
      'date-desc': (a, b) => new Date(b.dataset.date) - new Date(a.dataset.date),
      'date-asc': (a, b) => new Date(a.dataset.date) - new Date(b.dataset.date),
      'titre-az': (a, b) => a.dataset.titre.localeCompare(b.dataset.titre),
      'titre-za': (a, b) => b.dataset.titre.localeCompare(a.dataset.titre)
    };

    cartes.sort(sorter[sort] || sorter['date-desc']);

    // Filtre
    cartes.forEach(c => {
      let textMatch = true;
      if (search) {
        switch (field) {
          case 'titre':
            textMatch = c.dataset.titre.includes(search);
            break;
          case 'objet':
            textMatch = (c.dataset.objet || '').includes(search);
            break;
          case 'client':
            textMatch = (c.dataset.client || '').includes(search);
            break;
          default: // 'all'
            textMatch =
              c.dataset.titre.includes(search) ||
              (c.dataset.objet || '').includes(search) ||
              (c.dataset.client || '').includes(search);
        }
      }
      c.style.display = textMatch ? '' : 'none';
    });

    // Réorganise les cartes dans le conteneur
    cartes.forEach(c => container.appendChild(c));
  }

  // Écouteurs d'événements
  [searchFieldSel, searchInp, sortSel]
    .filter(el => el !== null)
    .forEach(el => el.addEventListener('input', applyFilters));

  // Applique les filtres une première fois
  applyFilters();
});
