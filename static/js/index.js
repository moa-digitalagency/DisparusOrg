document.addEventListener('DOMContentLoaded', function() {
    const mapElement = document.getElementById('main-map');
    if (!mapElement) return;

    const configElement = document.getElementById('index-config');
    const defaultFilter = configElement.dataset.defaultFilter;
    const moderatorWhatsapp = configElement.dataset.moderatorWhatsapp;
    const siteName = configElement.dataset.siteName;

    const map = L.map('main-map').setView([7.5, 15], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'OpenStreetMap'
    }).addTo(map);

    let userLocation = null;
    let markersLayer = L.layerGroup().addTo(map);
    const countryFilter = document.getElementById('country-filter');
    const typeFilter = document.getElementById('type-filter');
    const locationBadge = document.getElementById('user-location-badge');
    const moderatorLink = document.getElementById('moderator-link');

    // Initialize type filter from default setting
    if (typeFilter && defaultFilter) {
        typeFilter.value = defaultFilter;
    }

    const savedCountry = localStorage.getItem('disparus_country_filter');
    if (savedCountry && countryFilter) {
        countryFilter.value = savedCountry;
    }

    function fetchMapData() {
        const bounds = map.getBounds();
        const params = new URLSearchParams({
            min_lat: bounds.getSouth(),
            max_lat: bounds.getNorth(),
            min_lng: bounds.getWest(),
            max_lng: bounds.getEast(),
            type: typeFilter ? typeFilter.value : 'all',
            country: countryFilter ? countryFilter.value : ''
        });

        fetch(`/api/map-data?${params.toString()}`)
            .then(r => r.json())
            .then(data => {
                markersLayer.clearLayers();
                data.forEach(d => {
                    let color = '#ef4444';
                    if (['found', 'found_alive'].includes(d.status)) {
                        color = '#22c55e';
                    } else if (['deceased', 'found_deceased'].includes(d.status)) {
                        color = '#4b5563';
                    }
                    const marker = L.circleMarker([d.latitude, d.longitude], {
                        radius: 8,
                        fillColor: color,
                        color: '#fff',
                        weight: 2,
                        fillOpacity: 0.9
                    });

                    // Tooltip on hover (Photo + Name)
                    // escapeHtml is available globally from utils.js
                    const tooltipContent = '<div class="text-center p-1">' +
                        (d.photo_url ? '<img src="' + d.photo_url + '" class="w-16 h-16 mx-auto rounded-lg object-cover mb-1">' : '') +
                        '<div class="font-bold text-sm text-gray-900">' + escapeHtml(d.full_name) + '</div>' +
                        '<div class="text-xs text-gray-500">' + escapeHtml(d.city) + '</div>' +
                        '</div>';

                    marker.bindTooltip(tooltipContent, {
                        direction: 'top',
                        offset: [0, -5],
                        opacity: 1,
                        className: 'leaflet-tooltip-custom'
                    });

                    // Redirect on click
                    marker.on('click', function() {
                        window.location.href = '/disparu/' + d.public_id;
                    });

                    markersLayer.addLayer(marker);
                });
            })
            .catch(console.error);
    }

    function filterCards() {
        if (!countryFilter || !typeFilter) return;
        const selectedCountry = countryFilter.value;
        const selectedType = typeFilter.value;

        // Filter Cards
        const cards = document.querySelectorAll('.disparu-card');
        cards.forEach(card => {
            const cardType = card.dataset.personType;
            const cardCountry = card.dataset.country;
            let visible = true;

            if (selectedCountry && cardCountry !== selectedCountry) visible = false;
            if (selectedType && selectedType !== 'all') {
                if (selectedType === 'animal' && cardType !== 'animal') visible = false;
                if (selectedType === 'person' && cardType === 'animal') visible = false;
            }

            card.style.display = visible ? 'block' : 'none';
        });
    }

    function updateAll() {
        filterCards();
        fetchMapData();
    }

    if (countryFilter) {
        countryFilter.addEventListener('change', function() {
            localStorage.setItem('disparus_country_filter', this.value);
            updateAll();
        });
    }

    if (typeFilter) {
        typeFilter.addEventListener('change', function() {
            updateAll();
        });
    }

    map.on('moveend', fetchMapData);

    function openModeratorWhatsapp(e) {
        e.preventDefault();
        const number = moderatorWhatsapp;
        if (!number) {
            alert("Configuration manquante: Numero WhatsApp non defini");
            return;
        }

        let countryName = "inconnu";
        if (userLocation && locationBadge && locationBadge.textContent) {
            // Extract country from "City, Country" or just "Country"
            const parts = locationBadge.textContent.split(',');
            countryName = parts[parts.length - 1].trim();
        }

        const message = `Bonjour, j'ai vu la plateforme ${siteName} et j'aimerai être modérateur, je suis du ${countryName}.`;
        const url = `https://wa.me/${number.replace(/\D/g, '')}?text=${encodeURIComponent(message)}`;
        window.open(url, '_blank');
    }

    if (moderatorLink) {
        moderatorLink.addEventListener('click', openModeratorWhatsapp);
    }
    // Note: removed onclick attribute in HTML, handled here.

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                localStorage.setItem('disparus_user_lat', userLocation.lat);
                localStorage.setItem('disparus_user_lng', userLocation.lng);

                fetch('https://nominatim.openstreetmap.org/reverse?lat=' + userLocation.lat + '&lon=' + userLocation.lng + '&format=json')
                    .then(r => r.json())
                    .then(data => {
                        const city = data.address?.city || data.address?.town || data.address?.village || '';
                        const country = data.address?.country || '';
                        if ((city || country) && locationBadge) {
                            locationBadge.textContent = city ? city + ', ' + country : country;
                            locationBadge.classList.remove('hidden');
                        }
                    }).catch(() => {});

                if (countryFilter && !countryFilter.value) {
                    map.setView([userLocation.lat, userLocation.lng], 8);
                }
                updateAll();
            },
            function(error) {
                const savedLat = localStorage.getItem('disparus_user_lat');
                const savedLng = localStorage.getItem('disparus_user_lng');
                if (savedLat && savedLng) {
                    userLocation = { lat: parseFloat(savedLat), lng: parseFloat(savedLng) };
                }
                updateAll();
            },
            { enableHighAccuracy: false, timeout: 5000 }
        );
    } else {
        updateAll();
    }

    updateAll();
});
