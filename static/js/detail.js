document.addEventListener('DOMContentLoaded', function() {
    // --- Modals & Sharing ---
    const shareModal = document.getElementById('shareModal');
    const imageModal = document.getElementById('imageModal');
    const copySuccess = document.getElementById('copySuccess');

    // Functions
    function openShareModal() {
        if (shareModal) {
            shareModal.classList.remove('hidden');
            shareModal.classList.add('flex');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeShareModal() {
        if (shareModal) {
            shareModal.classList.add('hidden');
            shareModal.classList.remove('flex');
            document.body.style.overflow = 'auto';
        }
    }

    function copyLink() {
        navigator.clipboard.writeText(window.location.href).then(function() {
            if (copySuccess) {
                copySuccess.classList.remove('hidden');
                setTimeout(function() {
                    copySuccess.classList.add('hidden');
                }, 2000);
            }
        });
    }

    function openImageModal() {
        if (imageModal) {
            imageModal.classList.remove('hidden');
            imageModal.classList.add('flex');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeImageModal() {
        if (imageModal) {
            imageModal.classList.add('hidden');
            imageModal.classList.remove('flex');
            document.body.style.overflow = 'auto';
        }
    }

    // Event Listeners
    const btnOpenShare = document.getElementById('btn-open-share');
    if (btnOpenShare) btnOpenShare.addEventListener('click', openShareModal);

    const btnCloseShare = document.getElementById('btn-close-share');
    if (btnCloseShare) btnCloseShare.addEventListener('click', closeShareModal);

    const btnCopyLink = document.getElementById('btn-copy-link');
    if (btnCopyLink) btnCopyLink.addEventListener('click', copyLink);

    const detailPhoto = document.getElementById('detail-photo');
    if (detailPhoto) detailPhoto.addEventListener('click', openImageModal);

    const btnCloseImageModal = document.getElementById('btn-close-image-modal');
    if (btnCloseImageModal) btnCloseImageModal.addEventListener('click', closeImageModal);

    // Close on overlay click
    if (imageModal) {
        const imageContainer = imageModal.querySelector('.w-full');
        if (imageContainer) imageContainer.addEventListener('click', closeImageModal);
    }

    if (shareModal) {
        shareModal.addEventListener('click', function(e) {
            if (e.target === this) closeShareModal();
        });
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeImageModal();
            closeShareModal();
        }
    });

    // --- Contribution Form Toggle ---
    const contributionSelect = document.querySelector('select[name="contribution_type"]');
    if (contributionSelect) {
        contributionSelect.addEventListener('change', function() {
            const foundFields = document.getElementById('found-fields');
            if (foundFields) {
                foundFields.classList.toggle('hidden', this.value !== 'found');
            }
        });
    }

    // --- Data Loading ---
    const dataScript = document.getElementById('detail-data');
    if (!dataScript) return;

    let data;
    try {
        data = JSON.parse(dataScript.textContent);
    } catch(e) {
        console.error("Failed to parse detail data", e);
        return;
    }

    // --- Timer ---
    const timerDays = document.getElementById('timerDays');
    const timerHours = document.getElementById('timerHours');
    const timerMinutes = document.getElementById('timerMinutes');

    if (timerDays && data.person.isoDate) {
        const disappearanceDate = new Date(data.person.isoDate);
        const isMissing = data.person.isMissing;

        function updateTimer() {
            const endDateStr = data.person.updatedAt || data.person.isoDate;
            const now = isMissing ? new Date() : new Date(endDateStr);

            let diff = now - disappearanceDate;
            if (diff < 0) diff = 0;

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

            timerDays.textContent = days;
            timerHours.textContent = hours;
            timerMinutes.textContent = minutes;
        }

        updateTimer();
        if (isMissing) {
            setInterval(updateTimer, 60000);
        }
    }

    // --- Map ---
    const mapElement = document.getElementById('detail-map');
    if (mapElement) {
        const map = L.map('detail-map');
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'OpenStreetMap'
        }).addTo(map);

        const bounds = [];
        const markers = [];

        const redIcon = L.divIcon({
            className: 'custom-marker',
            html: '<div style="background-color: #DC2626; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });

        const blueIcon = L.divIcon({
            className: 'custom-marker',
            html: '<div style="background-color: #3B82F6; width: 18px; height: 18px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
            iconSize: [18, 18],
            iconAnchor: [9, 9]
        });

        const greenIcon = L.divIcon({
            className: 'custom-marker',
            html: '<div style="background-color: #22C55E; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>',
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });

        // Main Person Marker
        if (data.person.lat != null && data.person.lng != null) {
            const mainMarker = L.marker([data.person.lat, data.person.lng], {icon: redIcon}).addTo(map);
            const locLabel = data.translations.location_short;
            const city = data.person.city || '';
            const country = data.person.country || '';
            const dateStr = data.person.date || '';

            // escapeHtml is global
            mainMarker.bindPopup(`<strong>${escapeHtml(locLabel)}</strong><br>${escapeHtml(city)}, ${escapeHtml(country)}<br>${escapeHtml(dateStr)}`);
            bounds.push([data.person.lat, data.person.lng]);
            markers.push(mainMarker);
        }

        // Contributions Markers
        if (data.contributions) {
            data.contributions.forEach(c => {
                if (c.lat != null && c.lng != null) {
                    const icon = c.type === 'found' ? greenIcon : blueIcon;
                    const marker = L.marker([c.lat, c.lng], {icon: icon}).addTo(map);

                    const typeLabel = ({
                        'seen': data.translations.sighting,
                        'found': data.translations.person_found,
                        'info': data.translations.important_info,
                        'police': data.translations.police,
                        'other': data.translations.other
                    })[c.type] || c.type;

                    const locationName = c.locationName || '';
                    const createdAt = c.date || '';

                    marker.bindPopup(`<strong>${escapeHtml(typeLabel)}</strong><br>${escapeHtml(locationName)}<br>${escapeHtml(createdAt)}`);
                    bounds.push([c.lat, c.lng]);
                    markers.push(marker);
                }
            });
        }

        if (bounds.length > 0) {
            if (bounds.length === 1) {
                map.setView(bounds[0], 20);
            } else {
                map.fitBounds(bounds, {padding: [30, 30], maxZoom: 20});
            }
        } else {
            map.setView([0, 20], 3);
        }

        if (markers.length > 0) {
            markers[0].openPopup();
        }
    }
});
