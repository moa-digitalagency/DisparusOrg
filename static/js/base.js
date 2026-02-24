// PWA Service Worker Registration
document.addEventListener('DOMContentLoaded', function() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(function(err) {
            console.log('SW failed:', err);
        });
    }

    // Data Saver Optimization
    if (navigator.connection && navigator.connection.saveData) {
        console.log('Data Saver mode detected');
        document.body.classList.add('data-saver-active');

        const images = document.querySelectorAll('img.data-saver');
        const placeholder = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 200'%3E%3Crect width='100%25' height='100%25' fill='%23f3f4f6'/%3E%3Ctext x='50%25' y='50%25' font-family='sans-serif' font-size='16' fill='%236b7280' text-anchor='middle' dy='.3em'%3EClick to load image%3C/text%3E%3C/svg%3E";

        images.forEach(img => {
            // Save original src if not already present (e.g. from server rendering)
            if (!img.dataset.src) {
                img.dataset.src = img.src;
            }

            // Replace with placeholder
            img.src = placeholder;
            img.style.cursor = 'pointer';

            // Add click listener to load original
            img.addEventListener('click', function(e) {
                // If inside a link, prevent navigation for the first click
                if (this.closest('a')) {
                    e.preventDefault();
                    e.stopPropagation();
                }

                this.src = this.dataset.src;
                this.style.cursor = ''; // Reset cursor

                // Note: The event listener is removed automatically due to {once:true}
                // The next click will bubble up naturally.
            }, { once: true });
        });
    }
});
