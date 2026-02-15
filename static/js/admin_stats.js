document.addEventListener('DOMContentLoaded', function() {
    const periodSelect = document.querySelector('select[name="period"]');
    if (periodSelect) {
        periodSelect.addEventListener('change', function() {
            this.form.submit();
        });
    }
});
