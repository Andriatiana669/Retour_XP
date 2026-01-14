/*  dashboard/static/dashboard/js/liste_marche.js  */
document.addEventListener('DOMContentLoaded', () => {
    /* ---------- UTILS ---------- */
    const $ = s => document.querySelector(s);
    const $$ = s => [...document.querySelectorAll(s)];

    const table   = $('.marches-table tbody');
    const rows    = $$('tr[data-id]');
    const csrf    = $('[name=csrfmiddlewaretoken]')?.value;

    /* ---------- TRI ---------- */
    let sortState = {}; // {colIndex: 1|-1}
    $$('thead th').forEach((th, idx) => {
        if (idx > 3) return; // on ne tri que les 4 premières colonnes
        th.style.cursor = 'pointer';
        th.insertAdjacentHTML('beforeend', '<i class="fas fa-sort text-muted sort-icon"></i>');
        th.addEventListener('click', () => {
            const dir = (sortState[idx] || 1) * -1;
            sortState = {[idx]: dir};
            const sorted = [...rows].sort((a, b) => {
                let va = a.cells[idx].textContent.trim();
                let vb = b.cells[idx].textContent.trim();
                if (idx === 0) { // Date de MAJ
                    va = new Date(va.split('/').reverse().join('-'));
                    vb = new Date(vb.split('/').reverse().join('-'));
                }
                return va > vb ? dir : -dir;
            });
            sorted.forEach(r => table.appendChild(r));
        });
    });

    /* ---------- FILTRES ---------- */
    // 1) filtre Date
    const dateFilter = document.createElement('select');
    dateFilter.className = 'form-select form-select-sm d-inline-block w-auto me-3';
    dateFilter.innerHTML = `
        <option value="all">Toutes les dates</option>
        <option value="today">Aujourd'hui</option>
        <option value="week">Cette semaine</option>
        <option value="month">Ce mois</option>`;
    document.querySelector('.marches-table').before(dateFilter);

    // 2) filtre État
    const etatFilter = document.createElement('select');
    etatFilter.className = 'form-select form-select-sm d-inline-block w-auto me-3';
    etatFilter.innerHTML = '<option value="all">Tous les états</option>';
    const etats = [...new Set(rows.map(r => r.querySelector('select[name="etat"] option:checked')?.textContent.trim() || 'Non défini'))];
    etats.sort().forEach(e => etatFilter.innerHTML += `<option value="${e}">${e}</option>`);
    document.querySelector('.marches-table').before(etatFilter);

    // 3) filtre Resp
    const respFilter = document.createElement('select');
    respFilter.className = 'form-select form-select-sm d-inline-block w-auto me-3';
    respFilter.innerHTML = '<option value="all">Tous les resp</option>';
    const resps = [...new Set(rows.map(r => r.cells[3].textContent.trim()))];
    resps.sort().forEach(r => respFilter.innerHTML += `<option value="${r}">${r}</option>`);
    document.querySelector('.marches-table').before(respFilter);

    /* ---------- APPLICATION DES FILTRES ---------- */
    function applyFilters() {
        const dVal = dateFilter.value;
        const eVal = etatFilter.value;
        const rVal = respFilter.value;

        const now = new Date();
        const startOfWeek = new Date(now.setDate(now.getDate() - now.getDay()));
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

        rows.forEach(tr => {
            const dateTxt = tr.cells[0].textContent.trim();
            const dateRow = new Date(dateTxt.split('/').reverse().join('-'));
            const etatTxt = tr.querySelector('select[name="etat"] option:checked')?.textContent.trim() || 'Non défini';
            const respTxt = tr.cells[3].textContent.trim();

            let okDate = dVal === 'all' ||
                (dVal === 'today' && dateRow.toDateString() === new Date().toDateString()) ||
                (dVal === 'week' && dateRow >= startOfWeek) ||
                (dVal === 'month' && dateRow >= startOfMonth);

            let okEtat = eVal === 'all' || etatTxt === eVal;
            let okResp = rVal === 'all' || respTxt === rVal;

            tr.style.display = (okDate && okEtat && okResp) ? '' : 'none';
        });
    }
    dateFilter.addEventListener('change', applyFilters);
    etatFilter.addEventListener('change', applyFilters);
    respFilter.addEventListener('change', applyFilters);

    /* ---------- BOUTON « ANNULER » LIGNE PAR LIGNE ---------- */
    $$('button.reset-line').forEach(btn => {
        btn.addEventListener('click', () => {
            const tr     = btn.closest('tr[data-id]');
            const select = tr.querySelector('select.etat-select');
            const saved  = select.dataset.initial;   // valeur réelle en base
            select.value = saved || '';              // restore
        });
    });

    /* ---------- SAUVEGARDE RAPIDE DES ÉTATS ---------- */
    const saveBtn = $('#saveAllEtats');
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            let okCount = 0;
            for (const tr of rows) {
                if (tr.style.display === 'none') continue;

                const select   = tr.querySelector('select.etat-select');
                const initial  = select.dataset.initial || select.querySelector('option[selected]')?.value || '';
                const current  = select.value;

                if (current === initial) continue;   // ← RIEN DE CHANGÉ

                const id = tr.dataset.id;
                try {
                    const resp = await fetch(`/dashboard/marche/change-etat/${id}/`, {
                        method : 'POST',
                        headers: {'X-CSRFToken': csrf, 'Content-Type': 'application/json'},
                        body   : JSON.stringify({etat: current})
                    });
                    if (resp.ok) {
                        okCount++;
                        select.dataset.initial = current; // mémorise la nouvelle valeur
                    }
                } catch (e) { console.error(e); }
            }
            alert(`${okCount} état(s) mis à jour`);
            if (okCount) location.reload(); // recharge seulement si nécessaire
        });
    }
});