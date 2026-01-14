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

  if (btnGrand && btnPetit && container) {
    function setVue(grand) {
      container.classList.toggle('compact', !grand);
      btnGrand.classList.toggle('active', grand);
      btnPetit.classList.toggle('active', !grand);
      localStorage.setItem('carteVueGrand', grand);
    }
    btnGrand.addEventListener('click', () => setVue(true));
    btnPetit.addEventListener('click', () => setVue(false));
    setVue(localStorage.getItem('carteVueGrand') !== 'false');
  } else {
    console.warn("Un ou plusieurs éléments pour la bascule Grand/Petit sont introuvables.");
  }

  // --- TRI + FILTRE (avec choix du champ) ---
  const searchFieldSel = document.getElementById('searchField');
  const searchInp      = document.getElementById('searchCarte');
  const dateInp        = document.getElementById('filterDate');
  const sortSel        = document.getElementById('sortSelect');
  const cartes         = Array.from(document.querySelectorAll('.carte'));

  function applyFilters() {
    if (!searchFieldSel || !searchInp || !sortSel) {
      console.warn("Un ou plusieurs éléments de filtre/tri sont introuvables.");
      return;
    }

    const field   = searchFieldSel.value;
    const search  = searchInp.value.trim().toLowerCase();
    const dateVal = dateInp ? dateInp.value : null;
    const sort    = sortSel.value;

    // tri
    const sorter = {
      'date-desc': (a, b) => new Date(b.dataset.date) - new Date(a.dataset.date),
      'date-asc' : (a, b) => new Date(a.dataset.date) - new Date(b.dataset.date),
      'titre-az' : (a, b) => a.dataset.titre.localeCompare(b.dataset.titre),
      'titre-za' : (a, b) => b.dataset.titre.localeCompare(a.dataset.titre)
    };
    cartes.sort(sorter[sort] || sorter['date-desc']);

    // filtre
    cartes.forEach(c => {
      let textMatch = true;
      if (search) {
        switch (field) {
          case 'titre':
            textMatch = c.dataset.titre.toLowerCase().includes(search);
            break;
          case 'objet':
            textMatch = (c.dataset.objet || '').toLowerCase().includes(search);
            break;
          case 'client':
            textMatch = (c.dataset.client || '').toLowerCase().includes(search);
            break;
          default: // 'all'
            textMatch =
              c.dataset.titre.toLowerCase().includes(search) ||
              (c.dataset.objet || '').toLowerCase().includes(search) ||
              (c.dataset.client || '').toLowerCase().includes(search);
        }
      }
      const dateMatch = !dateVal || c.dataset.date === dateVal;
      c.style.display = (textMatch && dateMatch) ? '' : 'none';
    });

    // Réorganise les cartes dans le conteneur
    if (container) {
      cartes.forEach(c => container.appendChild(c));
    }
  }

  // Ajoute les écouteurs d'événements uniquement si les éléments existent
  [searchFieldSel, searchInp, dateInp, sortSel]
    .filter(el => el !== null)
    .forEach(el => el.addEventListener('input', applyFilters));

  // Applique les filtres une première fois
  applyFilters();
});
