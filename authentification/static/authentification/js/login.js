// authentification/static/authentification/js/login.js
document.addEventListener('DOMContentLoaded', () => {
    const form       = document.getElementById('loginForm');
    const userType   = document.getElementById('userType');
    const matGroup   = document.getElementById('matricule-group');
    const matInput   = document.getElementById('matricule');
    const mainBtn    = document.getElementById('mainBtn');
    const switchBtn  = document.getElementById('switchBtn');

    let responsableMode = false;

    /* bascule simple ↔ responsable */
    switchBtn.addEventListener('click', () => {
        responsableMode = !responsableMode;

        if (responsableMode) {  // mode responsable
            matGroup.style.display = 'block';
            matInput.required = true;
            userType.value = 'responsable';

            mainBtn.textContent = 'Se connecter (responsable)';
            mainBtn.className   = 'btn-responsable';

            switchBtn.textContent = 'Annuler';
            switchBtn.className   = 'btn-simple';
            matInput.focus();
        } else {                // mode simple
            matGroup.style.display = 'none';
            matInput.required = false;
            matInput.value    = '';
            userType.value    = 'simple';

            mainBtn.textContent = 'Se connecter';
            mainBtn.className   = 'btn-simple';

            switchBtn.textContent = 'Responsable';
            switchBtn.className   = 'btn-responsable';
        }
    });

    /* validation avant envoi */
    form.addEventListener('submit', e => {
        if (userType.value === 'responsable' && !matInput.value.trim()) {
            e.preventDefault();
            alert('Veuillez entrer votre matricule');
            matInput.focus();
        }
    });
});