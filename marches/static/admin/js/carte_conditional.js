// marches/static/admin/js/carte_conditional.js
document.addEventListener('DOMContentLoaded', function () {
    const select = document.querySelector('#id_solution');
    if (!select) return;
    const fieldset = select.closest('.field-solution');
    if (!fieldset) return;

    function toggle() {
        const option = select.selectedOptions[0];
        fieldSet.classList.toggle('show-demarche', option && option.dataset.demand === '1');
    }
    select.addEventListener('change', toggle);
    toggle(); // au chargement
});