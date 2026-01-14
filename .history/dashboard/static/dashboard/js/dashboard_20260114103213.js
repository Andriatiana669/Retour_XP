// Filtre et recherche en temps réel
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchMarche');
    const filterSelect = document.getElementById('filterProjets');
    const marcheCards = document.querySelectorAll('.marche-card');

    // Recherche
    searchInput.addEventListener('input', function () {
        const searchTerm = this.value.toLowerCase();
        marcheCards.forEach(card => {
            const title       = card.querySelector('h3').textContent.toLowerCase();
            const description = card.querySelector('p')?.textContent.toLowerCase() || '';
            const projCount   = card.querySelector('.projet-count').textContent.toLowerCase();

            const matches =
                title.includes(searchTerm) ||
                description.includes(searchTerm) ||
                projCount.includes(searchTerm);

            card.style.display = matches ? 'flex' : 'none';
        });
    });

    // Filtre par nombre de projets
    filterSelect.addEventListener('change', function() {
        const minProjets = this.value;
        marcheCards.forEach(card => {
            const projetCount = parseInt(card.querySelector('.projet-count').textContent);
            if (minProjets === 'all') {
                card.style.display = 'flex';
            } else {
                const min = parseInt(minProjets);
                card.style.display = projetCount >= min ? 'flex' : 'none';
            }
        });
    });

    // Animation au clic sur les cartes
    marcheCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.classList.contains('btn-voir')) {
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 200);
            }
        });
    });
});
