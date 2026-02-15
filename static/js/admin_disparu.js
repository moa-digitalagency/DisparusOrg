document.addEventListener('DOMContentLoaded', function() {
    const config = document.getElementById('admin-disparu-config');
    if (!config) return;

    const countriesCities = JSON.parse(config.dataset.countriesCities);
    const initialLat = parseFloat(config.dataset.lat);
    const initialLng = parseFloat(config.dataset.lng);
    const selectCityLabel = config.dataset.selectCity;
    const noResultLabel = config.dataset.noResult;

    // Photo Preview
    const photoInput = document.querySelector('input[name="photo"]');
    if (photoInput) {
        photoInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('photo_preview').src = e.target.result;
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Country/City
    const countrySelect = document.getElementById('country-select');
    const citySelect = document.getElementById('city-select');

    if (countrySelect && citySelect) {
        countrySelect.addEventListener('change', function() {
            const country = this.value;
            citySelect.innerHTML = `<option value="">${selectCityLabel}</option>`;
            if (country && countriesCities[country]) {
                countriesCities[country].forEach(function(city) {
                    const option = document.createElement('option');
                    option.value = city;
                    option.textContent = city;
                    citySelect.appendChild(option);
                });
            }
        });
    }

    // Person Type
    const personTypeSelect = document.getElementById('person_type');
    const animalFields = document.getElementById('animal_fields');
    if (personTypeSelect && animalFields) {
        personTypeSelect.addEventListener('change', function() {
            animalFields.classList.toggle('hidden', this.value !== 'animal');
        });
    }

    // Map
    const mapElement = document.getElementById('map');
    let map, marker;

    if (mapElement) {
        const zoom = initialLat ? 13 : 2;
        map = L.map('map').setView([initialLat, initialLng], zoom);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        if (initialLat && initialLng) {
            marker = L.marker([initialLat, initialLng], {draggable: true}).addTo(map);
            marker.on('dragend', updateLatLng);
        }

        map.on('click', function(e) {
            if (marker) {
                marker.setLatLng(e.latlng);
            } else {
                marker = L.marker(e.latlng, {draggable: true}).addTo(map);
                marker.on('dragend', updateLatLng);
            }
            updateLatLng({target: marker});
        });
    }

    function updateLatLng(e) {
        const latlng = e.target.getLatLng();
        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        if (latInput) latInput.value = latlng.lat;
        if (lngInput) lngInput.value = latlng.lng;
    }

    // Address Search
    function searchAddress() {
        const input = document.getElementById('address_search');
        const errorMsg = document.getElementById('search_error');
        const query = input ? input.value : '';

        if (!query || query.length < 3) return;

        if (errorMsg) errorMsg.classList.add('hidden');

        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`, {
            headers: {
                'User-Agent': 'Disparus.org Admin Panel'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const result = data[0];
                const lat = parseFloat(result.lat);
                const lon = parseFloat(result.lon);

                document.getElementById('latitude').value = lat;
                document.getElementById('longitude').value = lon;

                const latlng = [lat, lon];
                if (marker) {
                    marker.setLatLng(latlng);
                } else {
                    marker = L.marker(latlng, {draggable: true}).addTo(map);
                    marker.on('dragend', updateLatLng);
                }
                map.setView(latlng, 16);
            } else {
                if (errorMsg) {
                    errorMsg.textContent = noResultLabel;
                    errorMsg.classList.remove('hidden');
                }
            }
        })
        .catch(err => {
            console.error(err);
            if (errorMsg) {
                errorMsg.textContent = "Erreur de recherche";
                errorMsg.classList.remove('hidden');
            }
        });
    }

    const searchBtn = document.getElementById('btn_search_address');
    if (searchBtn) searchBtn.addEventListener('click', searchAddress);

    const searchInput = document.getElementById('address_search');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchAddress();
            }
        });
    }
});
