document.addEventListener('DOMContentLoaded', function() {
    const confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const msg = this.dataset.confirm;
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });
});
