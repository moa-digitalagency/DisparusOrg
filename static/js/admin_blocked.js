document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('detailsModal');
    const content = document.getElementById('modal-content');
    const backdrop = document.getElementById('modal-backdrop');
    const closeBtn = document.getElementById('btn-close-modal');

    function showDetails(jsonStr) {
        // Use robust parser from utils.js that handles Python-style strings
        const jsonObj = robustJSONParse(jsonStr);
        if (jsonObj !== null) {
            content.textContent = JSON.stringify(jsonObj, null, 2);
        } else {
            content.textContent = jsonStr || '';
        }
        modal.classList.remove('hidden');
    }

    function closeModal() {
        modal.classList.add('hidden');
    }

    const detailButtons = document.querySelectorAll('.btn-show-details');
    detailButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            showDetails(this.dataset.details);
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    if (backdrop) {
        backdrop.addEventListener('click', closeModal);
    }
});
