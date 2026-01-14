document.addEventListener('DOMContentLoaded', () => {
    const searchBar  = document.getElementById('searchBar');
    const typeFilter = document.getElementById('typeFilter');

    function reload() {
        const params = new URLSearchParams();
        const q = searchBar.value.trim();
        if (q) params.set('q', q);
        if (typeFilter.value !== 'all') params.set('type', typeFilter.value);
        window.location.search = params.toString();
    }

    // Recherche seulement quand on appuie sur Entrée
    searchBar.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            reload();
        }
    });

    typeFilter.addEventListener('change', reload);
});
