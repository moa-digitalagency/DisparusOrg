document.addEventListener('DOMContentLoaded', function() {
    const config = document.getElementById('admin-map-config');
    if (!config) return;

    const reportLabel = config.dataset.labelReports;

    const mapElement = document.getElementById('admin-map');
    if (!mapElement) return;

    const map = L.map('admin-map').setView([7.5, 15], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'OpenStreetMap'
    }).addTo(map);

    const hoverCard = document.getElementById('hover-card');
    const adminCountryFilter = document.getElementById('admin-country-filter');
    const adminTypeFilter = document.getElementById('admin-type-filter');
    const adminCount = document.getElementById('admin-count');
    let markersLayer = L.layerGroup().addTo(map);

    const savedAdminCountry = localStorage.getItem('disparus_admin_country_filter');
    if (savedAdminCountry && adminCountryFilter) {
        adminCountryFilter.value = savedAdminCountry;
    }

    function fetchAdminMapData() {
        const bounds = map.getBounds();
        const params = new URLSearchParams({
            min_lat: bounds.getSouth(),
            max_lat: bounds.getNorth(),
            min_lng: bounds.getWest(),
            max_lng: bounds.getEast(),
            type: adminTypeFilter ? adminTypeFilter.value : '',
            country: adminCountryFilter ? adminCountryFilter.value : ''
        });

        fetch(`/api/map-data?${params.toString()}`)
            .then(r => r.json())
            .then(data => {
                markersLayer.clearLayers();

                if (adminCount) {
                    adminCount.textContent = data.length + ' ' + reportLabel;
                }

                data.forEach(d => {
                    let color = '#ef4444'; // missing (red)
                    if (['found', 'found_alive'].includes(d.status)) {
                        color = '#22c55e'; // green
                    } else if (['deceased', 'found_deceased'].includes(d.status)) {
                        color = '#4b5563'; // gray
                    } else if (d.is_flagged) {
                        color = '#f97316'; // orange
                    }

                    const marker = L.circleMarker([d.latitude, d.longitude], {
                        radius: 10,
                        fillColor: color,
                        color: '#fff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.9
                    });

                    // Tooltip on hover (Photo + Name)
                    // escapeHtml is global from utils.js
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

                    marker.on('click', function() {
                        window.location.href = '/disparu/' + d.public_id;
                    });
                    markersLayer.addLayer(marker);
                });
            })
            .catch(console.error);
    }

    if (adminCountryFilter) {
        adminCountryFilter.addEventListener('change', function() {
            localStorage.setItem('disparus_admin_country_filter', this.value);
            fetchAdminMapData();
        });
    }

    if (adminTypeFilter) {
        adminTypeFilter.addEventListener('change', fetchAdminMapData);
    }

    map.on('moveend', fetchAdminMapData);

    if (hoverCard) {
        hoverCard.addEventListener('mouseleave', function() {
            hoverCard.classList.add('hidden');
        });
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                if (adminCountryFilter && !adminCountryFilter.value) {
                    map.setView([position.coords.latitude, position.coords.longitude], 8);
                }
            },
            function() {},
            { enableHighAccuracy: false, timeout: 5000 }
        );
    }

    fetchAdminMapData();
});
