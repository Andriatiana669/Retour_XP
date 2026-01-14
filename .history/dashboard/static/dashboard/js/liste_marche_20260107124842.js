// Filtre et recherche en temps réel
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchMarche');
    const filterSelect = document.getElementById('filterProjets');
    const marcheCards = document.querySelectorAll('.marche-card');

    // Recherche
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        marcheCards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            card.style.display = title.includes(searchTerm) ? 'flex' : 'none';
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

/* ---------- Sauvegarde rapide des états ---------- */
document.addEventListener('DOMContentLoaded', () => {
    const saveBtn = document.getElementById('saveAllEtats');
    saveBtn.addEventListener('click', async () => {
        const rows = document.querySelectorAll('tr[data-id]');
        for (const tr of rows) {
            const id   = tr.dataset.id;
            const select = tr.querySelector('select[name="etat"]');
            const etatId = select.value;
            await fetch(`{% url 'dashboard:change_etat' 0 %}`.replace('0', id), {
                method : 'POST',
                headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                body   : JSON.stringify({etat: etatId}),
            });
        }
        location.reload();          // simple mais efficace
    });
});