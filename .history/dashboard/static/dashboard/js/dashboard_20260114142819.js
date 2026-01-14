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

    /* petite icône pour les badges */
    const icon = (i, t) => `<i class="${i}" title="${t}"></i>`;

    searchInput.addEventListener('input', () => {
        const needle = norm(searchInput.value);
        if (!needle) {
            detailsZone.classList.add('d-none');
            marcheCards.forEach(c => c.style.display = 'flex');
            return;
        }

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

            let detailHtml = '';

            detailArr.forEach(md => {
                const mdFlat  = flatten(md) + ' ' + (md.nom_marche || '');
                let   mdMatch = norm(mdFlat).includes(needle);

                /* ----- CARTES ----- */
                let carteHtml = '';
                (md.cartes || []).forEach(c => {
                    const cFlat = flatten(c);
                    if (norm(cFlat).includes(needle)) {
                        hasResults = ok = true;
                        carteHtml += `
                          <div class="result-item d-flex justify-content-between align-items-start">
                            <div>
                              <div class="fw-bold">${highlight(c.titre, needle)}</div>
                              <small class="text-muted">
                                ${icon('fas fa-user', 'Client')} ${highlight(c.client_carte, needle)}
                                ${c.nom_dossier ? icon('fas fa-folder', 'Dossier') + ' ' + highlight(c.nom_dossier, needle) : ''}
                              </small>
                            </div>
                            <a href="${c.url}" class="btn btn-sm btn-outline-primary ms-2">Voir</a>
                          </div>`;
                    }
                });

                if (mdMatch || carteHtml) {
                    hasResults = true;
                    const nomMarcheTag = md.nom_marche
                        ? `<div class="mb-1"><span class="badge bg-secondary">${icon('fas fa-tag', 'Nom marché')} ${highlight(md.nom_marche, needle)}</span></div>`
                        : '';
                    detailHtml += `
                      <div class="result-group">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                          <h5 class="mb-0">${icon('fas fa-folder-open', 'Marché détaillé')} ${highlight(md.titre, needle)}</h5>
                          <a href="${md.url}" class="btn btn-primary btn-sm">Voir le marché</a>
                        </div>
                        ${nomMarcheTag}
                        <div class="ms-3 mb-2">
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