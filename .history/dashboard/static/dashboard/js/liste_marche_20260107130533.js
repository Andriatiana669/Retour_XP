/*  dashboard/static/dashboard/js/liste_marche.js  */
/*  Nouvelle version – compatible avec le HTML actuel  */

document.addEventListener('DOMContentLoaded', () => {
    /* ---------- Sauvegarde rapide des états ---------- */
    const saveBtn = document.getElementById('saveAllEtats');
    if (!saveBtn) return;                  // sécurité si le bouton n’existe pas

    saveBtn.addEventListener('click', async () => {
        const rows = document.querySelectorAll('tr[data-id]');
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrf) { alert('Token CSRF introuvable'); return; }

        let okCount = 0;
        for (const tr of rows) {
            const id     = tr.dataset.id;
            const select = tr.querySelector('select[name="etat"]');
            const etatId = select.value;

            try {
                const resp = await fetch(`/dashboard/marche/change-etat/${id}/`, {
                    method : 'POST',
                    headers: {
                        'X-CSRFToken': csrf,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({etat: etatId})
                });
                if (resp.ok) okCount++;
            } catch (e) {
                console.error('Erreur réseau', e);
            }
        }
        alert(`${okCount} état(s) mis à jour`);
        location.reload();          // rafraîchit la page
    });
});