document.addEventListener('DOMContentLoaded', function() {
    // Demo Delete
    const formDeleteDemo = document.getElementById('form-delete-demo');
    if (formDeleteDemo) {
        formDeleteDemo.addEventListener('submit', function(e) {
            const msg = this.dataset.confirmMsg;
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    }

    // Full Delete
    const formDeleteAll = document.getElementById('form-delete-all');
    if (formDeleteAll) {
        formDeleteAll.addEventListener('submit', function(e) {
            const countrySelect = document.getElementById('delete-country');
            const config = document.getElementById('admin-data-config');

            if (!countrySelect || !config) return;

            const country = countrySelect.value;
            let msg = '';
            if (country) {
                msg = config.dataset.msgSpecific.replace('{country}', country);
            } else {
                msg = config.dataset.msgAll;
            }

            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    }
});
