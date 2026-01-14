document.addEventListener('DOMContentLoaded', () => {
    const searchInput   = document.getElementById('searchMarche');
    const marcheCards   = document.querySelectorAll('.marche-card');
    const detailsZone   = document.getElementById('detailsResults');
    const resultsContainer = document.getElementById('resultsContainer');

    const norm = s => s.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '');

    const flatten = obj => JSON.stringify(obj).replace(/"|{|}/g, ' ');

    const highlight = (haystack, needle) => {
        if (!needle) return haystack;
        const re = new RegExp(`(${needle})`, 'gi');
        return haystack.replace(re, '<mark class="highlight">$1</mark>');
    };

    searchInput.addEventListener('input', () => {
        const needle = norm(searchInput.value);

        /* -------- tout effacé : on remet tout et on sort -------- */
        if (!needle) {
            detailsZone.classList.add('d-none');
            marcheCards.forEach(c => c.style.display = 'flex');
            return;
        }

        /* -------- recherche classique -------- */
        let hasResults = false;
        resultsContainer.innerHTML = '';

        marcheCards.forEach(card => {
            const mgId   = card.dataset.id;
            const txtAll = [
                card.querySelector('h3').textContent,
                card.querySelector('p')?.textContent || '',
                card.querySelector('.projet-count').textContent
            ].join(' ');

            let ok = norm(txtAll).includes(needle);
            const detailArr = window.searchData[mgId] || [];
            let detailHtml  = '';

            detailArr.forEach(md => {
                const mdFlat  = flatten(md);
                const carteArr = md.cartes || [];
                let mdMatch   = norm(mdFlat).includes(needle);
                let carteHtml = '';

                carteArr.forEach(c => {
                    const cFlat = flatten(c);
                    if (norm(cFlat).includes(needle)) {
                        hasResults = ok = true;
                        carteHtml += `
                          <div class="result-item">
                            <i class="fas fa-file-alt me-1"></i>
                            ${highlight(c.titre, needle)}
                            <small class="text-muted d-block">Carte – ${highlight(c.client_carte, needle)}</small>
                          </div>`;
                    }
                });

                if (mdMatch || carteHtml) {
                    hasResults = true;
                    detailHtml += `
                      <div class="result-group">
                          <h5><i class="fas fa-folder-open me-1"></i>
                              ${highlight(md.titre, needle)}</h5>
                          <div class="ms-3">
                              ${highlight(md.objet + ' ' + md.description + ' ' + md.resp + ' ' + md.clients + ' ' + md.prestations, needle)}
                          </div>
                          ${carteHtml}
                      </div>`;
                }
            });

            if (detailHtml) resultsContainer.insertAdjacentHTML('beforeend', detailHtml);
            card.style.display = ok ? 'flex' : 'none';
        });

        detailsZone.classList.toggle('d-none', !hasResults);
    });

    marcheCards.forEach(c => c.addEventListener('click', e => {
        if (!e.target.classList.contains('btn-voir')) {
            c.style.transform = 'scale(.98)';
            setTimeout(() => c.style.transform = '', 200);
        }
    }));
});