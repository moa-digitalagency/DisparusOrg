document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('detailsModal');
    const content = document.getElementById('modal-content');
    const backdrop = document.getElementById('modal-backdrop');
    const closeBtn = document.getElementById('btn-close-modal');

    function showDetails(jsonStr) {
        try {
            // Replace single quotes with double quotes if needed, though usually valid JSON uses double quotes
            // Jinja might output python dict string representation if not careful, but metadata_json suggests it's JSON.
            // If it's single quoted from python string, we might need fix.
            // But let's assume valid JSON first.
            let jsonObj = JSON.parse(jsonStr);
            content.textContent = JSON.stringify(jsonObj, null, 2);
        } catch (e) {
            content.textContent = jsonStr;
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
