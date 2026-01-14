document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchMarche');
    const marcheCards = document.querySelectorAll('.marche-card');

    // normalise une chaîne : minuscule + sans accents
    const norm = s => s.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '');

    searchInput.addEventListener('input', () => {
        const needle = norm(searchInput.value);

        marcheCards.forEach(card => {
            const mgId   = card.dataset.id;          // ← on ajoutera cet attribut
            const txtAll = [
                card.querySelector('h3').textContent,
                card.querySelector('p')?.textContent || '',
                card.querySelector('.projet-count').textContent
            ].join(' ');

            // 1) texte visible du GLOBAL
            let ok = norm(txtAll).includes(needle);

            // 2) on fouille dans les détails / cartes cachés
            if (!ok && window.searchData[mgId]) {
                const flat = JSON.stringify(window.searchData[mgId]);
                ok = norm(flat).includes(needle);
            }

            card.style.display = ok ? 'flex' : 'none';
        });
    });

    // petite animation déjà présente
    marcheCards.forEach(c => c.addEventListener('click', e => {
        if (!e.target.classList.contains('btn-voir')) {
            c.style.transform = 'scale(.98)';
            setTimeout(() => c.style.transform = '', 200);
        }
    }));
});