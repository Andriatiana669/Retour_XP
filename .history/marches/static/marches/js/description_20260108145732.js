document.addEventListener('DOMContentLoaded', () => {
  /* ---------- Copie + feedback visuel ---------- */
  document.querySelectorAll('.btn-copy').forEach(btn => {
    btn.addEventListener('click', async () => {
      const text = btn.dataset.contenu;
      try {
        await navigator.clipboard.writeText(text);
        const icone = btn.querySelector('i');
        icone.classList.replace('fa-copy', 'fa-check');
        setTimeout(() => icone.classList.replace('fa-check', 'fa-copy'), 1200);
      } catch (err) {
        console.error('Copie échouée', err);
      }
    });
  });

  /* ---------- Bascule Grand / Petit ---------- */
  const btnGrand = document.getElementById('btnGrand');
  const btnPetit = document.getElementById('btnPetit');
  const container = document.getElementById('cartesContainer');

  function setVue(grand) {
    container.classList.toggle('compact', !grand);
    btnGrand?.classList.toggle('active', grand);
    btnPetit?.classList.toggle('active', !grand);
    localStorage.setItem('carteVueGrand', grand);
  }
  btnGrand?.addEventListener('click', () => setVue(true));
  btnPetit?.addEventListener('click', () => setVue(false));
  setVue(localStorage.getItem('carteVueGrand') !== 'false');

  /* ---------- Filtres & Tri ---------- */
  const searchFieldSel = document.getElementById('searchField');
  const searchInp = document.getElementById('searchCarte');
  const sortSel = document.getElementById('sortSelect');
  const resetBtn = document.getElementById('resetFilters');
  const cartes = Array.from(document.querySelectorAll('.carte'));

  function saveFilters() {
    if (searchFieldSel) localStorage.setItem('searchField', searchFieldSel.value);
    if (searchInp) localStorage.setItem('searchCarte', searchInp.value);
    if (sortSel) localStorage.setItem('sortSelect', sortSel.value);
  }

  function restoreFilters() {
    if (searchFieldSel) searchFieldSel.value = localStorage.getItem('searchField') || 'all';
    if (searchInp) searchInp.value = localStorage.getItem('searchCarte') || '';
    if (sortSel) sortSel.value = localStorage.getItem('sortSelect') || 'date-desc';
  }

  function applyFilters() {
    const field = searchFieldSel?.value || 'all';
    const search = searchInp?.value.trim().toLowerCase() || '';
    const sort = sortSel?.value || 'date-desc';

    // tri
    const sorter = {
      'date-desc': (a, b) => new Date(b.dataset.date) - new Date(a.dataset.date),
      'date-asc': (a, b) => new Date(a.dataset.date) - new Date(b.dataset.date),
      'titre-az': (a, b) => a.dataset.titre.localeCompare(b.dataset.titre),
      'titre-za': (a, b) => b.dataset.titre.localeCompare(a.dataset.titre)
    };
    cartes.sort(sorter[sort] || sorter['date-desc']);

    // filtre
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

    // ré-organise
    cartes.forEach(c => container.appendChild(c));
    saveFilters();
  }

  // écouteurs
  searchFieldSel?.addEventListener('input', applyFilters);
  searchInp?.addEventListener('input', applyFilters);
  sortSel?.addEventListener('input', applyFilters);
  resetBtn?.addEventListener('click', () => {
    if (searchFieldSel) searchFieldSel.value = 'all';
    if (searchInp) searchInp.value = '';
    if (sortSel) sortSel.value = 'date-desc';
    applyFilters();
  });

  restoreFilters();
  applyFilters();
});