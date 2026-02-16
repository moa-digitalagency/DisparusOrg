document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('detailsModal');
    const content = document.getElementById('modal-content');
    const backdrop = document.getElementById('modal-backdrop');
    const closeBtn = document.getElementById('btn-close-modal');

    function showDetails(jsonStr) {
        try {
            // Try standard JSON parse first
            let jsonObj = JSON.parse(jsonStr);
            content.textContent = JSON.stringify(jsonObj, null, 2);
        } catch (e) {
            // If standard parsing fails, attempt to fix common Python string representation issues
            // (e.g. single quotes, True/False/None)
            try {
                if (!jsonStr) throw e;
                let fixedStr = jsonStr
                    .replace(/'/g, '"')
                    .replace(/\bTrue\b/g, 'true')
                    .replace(/\bFalse\b/g, 'false')
                    .replace(/\bNone\b/g, 'null');
                let jsonObj = JSON.parse(fixedStr);
                content.textContent = JSON.stringify(jsonObj, null, 2);
            } catch (e2) {
                // If repair fails, fallback to raw string
                content.textContent = jsonStr;
            }
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
