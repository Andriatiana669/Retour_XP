// dashboard.js
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

    searchBar.addEventListener('change', reload);
    typeFilter.addEventListener('change', reload);
});