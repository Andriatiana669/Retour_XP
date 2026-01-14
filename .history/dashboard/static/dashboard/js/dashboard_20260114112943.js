// dashboard.js
document.addEventListener('DOMContentLoaded', () => {
    const searchBar   = document.getElementById('searchBar');
    const typeFilter  = document.getElementById('typeFilter');

    // Recharge la page avec les paramètres GET appropriés
    function reload() {
        const params = new URLSearchParams();
        const q = searchBar.value.trim();
        if (q) params.set('q', q);
        if (typeFilter.value !== 'all') params.set('type', typeFilter.value);
        window.location.search = params.toString();
    }

    searchBar.addEventListener('change', reload);
    typeFilter.addEventListener('change', reload);

    // Petite animation au clic sur les cartes (facultatif)
    document.querySelectorAll('.result-card').forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.classList.contains('btn-voir')) {
                this.style.transform = 'scale(0.98)';
                setTimeout(() => { this.style.transform = ''; }, 200);
            }
        });
    });
});