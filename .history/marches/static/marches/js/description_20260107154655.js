/* Copie le texte d’une carte dans le presse-papiers + feedback visuel */
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-copy').forEach(btn => {
        btn.addEventListener('click', async () => {
            const text = btn.dataset.contenu;
            try {
                await navigator.clipboard.writeText(text);
                btn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => btn.innerHTML = '<i class="far fa-copy"></i>', 1200);
            } catch (err) {
                console.error('Copie échouée', err);
            }
        });
    });
});