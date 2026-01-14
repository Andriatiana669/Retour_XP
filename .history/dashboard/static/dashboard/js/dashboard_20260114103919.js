/* dashboard.js – recherche + filtre par champ + animation clic */
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchMarche');
    const fieldSelect = document.getElementById('searchField');
    const cards = document.querySelectorAll('.marche-card');

    /* filtre + recherche */
    function filterCards() {
        const term = searchInput.value.trim().toLowerCase();
        const field = fieldSelect.value;

        cards.forEach(card => {
            const sources = {
                all: [
                    card.dataset.titre,
                    card.dataset.nom_marche,
                    card.dataset.prestation,
                    card.dataset.client,
                    card.dataset.resp,
                    card.dataset.carte
                ].join(' '),
                titre: card.dataset.titre,
                nom_marche: card.dataset.nom_marche,
                prestation: card.dataset.prestation,
                client: card.dataset.client,
                resp: card.dataset.resp,
                carte: card.dataset.carte
            };
            const haystack = sources[field] || sources.all;
            card.style.display = haystack.includes(term) ? 'flex' : 'none';
        });
    }

    searchInput.addEventListener('input', filterCards);
    fieldSelect.addEventListener('change', filterCards);
    filterCards(); // premier affichage

    /* animation clic (hors bouton) */
    cards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.classList.contains('btn-voir')) {
                this.style.transform = 'scale(0.98)';
                setTimeout(() => this.style.transform = '', 200);
            }
        });
    });
});