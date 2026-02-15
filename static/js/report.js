document.addEventListener('DOMContentLoaded', function() {
    const config = document.getElementById('report-config');
    if (!config) return;

    const countriesCities = JSON.parse(config.dataset.countriesCities);
    const translations = {
        geoError: config.dataset.geoError,
        addressNotFound: config.dataset.addressNotFound,
        searchError: config.dataset.searchError,
        selectCity: config.dataset.selectCity,
        animalName: config.dataset.labelAnimalName,
        animalClothing: config.dataset.labelAnimalClothing,
        maleAnimal: config.dataset.labelMaleAnimal,
        femaleAnimal: config.dataset.labelFemaleAnimal,
        firstName: config.dataset.labelFirstName,
        clothing: config.dataset.labelClothing,
        male: config.dataset.labelMale,
        female: config.dataset.labelFemale
    };

    // --- Auto-detect IP Location ---
    const countrySelect = document.getElementById('country-select');
    const citySelect = document.getElementById('city-select');

    if (countrySelect && !countrySelect.value) {
        fetch('/api/geo/ip')
            .then(res => res.json())
            .then(data => {
                if (data.country) {
                    for (let i = 0; i < countrySelect.options.length; i++) {
                        if (countrySelect.options[i].value.toLowerCase() === data.country.toLowerCase()) {
                            countrySelect.selectedIndex = i;
                            countrySelect.dispatchEvent(new Event('change'));

                            setTimeout(() => {
                                if (data.city && citySelect) {
                                    for (let j = 0; j < citySelect.options.length; j++) {
                                        if (citySelect.options[j].value.toLowerCase() === data.city.toLowerCase()) {
                                            citySelect.selectedIndex = j;
                                            break;
                                        }
                                    }
                                }
                            }, 300);
                            break;
                        }
                    }
                }
            })
            .catch(err => console.log('IP Geo failed', err));
    }

    // --- Country/City Dependent Dropdown ---
    if (countrySelect && citySelect) {
        countrySelect.addEventListener('change', function() {
            const country = this.value;
            citySelect.innerHTML = `<option value="">${translations.selectCity}</option>`;

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

    // --- Map Logic ---
    const mapElement = document.getElementById('location-map');
    let locationMap, marker;

    if (mapElement) {
        locationMap = L.map('location-map').setView([7.5, 15], 4);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'OpenStreetMap'
        }).addTo(locationMap);

        locationMap.on('click', function(e) {
            setLocation(e.latlng.lat, e.latlng.lng);
        });
    }

    function setLocation(lat, lng) {
        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        const display = document.getElementById('coords-display');

        if (latInput) latInput.value = lat;
        if (lngInput) lngInput.value = lng;
        if (display) display.textContent = lat.toFixed(4) + ', ' + lng.toFixed(4);

        if (locationMap) {
            if (marker) {
                marker.setLatLng([lat, lng]);
            } else {
                marker = L.marker([lat, lng]).addTo(locationMap);
            }
            locationMap.setView([lat, lng], 16);
        }
    }

    // --- Search Address ---
    function searchAddress() {
        const input = document.getElementById('address-search');
        const btn = document.getElementById('btn-search-address');
        const query = input ? input.value : '';
        const country = countrySelect ? countrySelect.value : '';
        const city = citySelect ? citySelect.value : '';

        if (!query) return;

        const originalBtnContent = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';

        let fullQuery = query;
        if (city) fullQuery += `, ${city}`;
        if (country) fullQuery += `, ${country}`;

        let searchUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(fullQuery)}`;

        fetch(searchUrl)
            .then(response => response.json())
            .then(data => {
                if (data && data.length > 0) {
                    const lat = parseFloat(data[0].lat);
                    const lon = parseFloat(data[0].lon);
                    setLocation(lat, lon);
                } else {
                    alert(translations.addressNotFound);
                }
            })
            .catch(err => {
                console.error(err);
                alert(translations.searchError);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = originalBtnContent;
            });
    }

    const searchBtn = document.getElementById('btn-search-address');
    if (searchBtn) {
        searchBtn.addEventListener('click', searchAddress);
    }

    const searchInput = document.getElementById('address-search');
    if (searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchAddress();
            }
        });
    }

    // --- Geolocation ---
    function getGeoLocation() {
        const btn = document.getElementById('btn-geolocate');
        if (!btn) return;

        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Localisation...';

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(pos) {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                setLocation(lat, lng);

                fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data && data.address) {
                            const country = data.address.country;
                            const city = data.address.city || data.address.town || data.address.village || data.address.municipality;

                            if (country && countrySelect) {
                                for (let i = 0; i < countrySelect.options.length; i++) {
                                    if (countrySelect.options[i].text.toLowerCase() === country.toLowerCase() ||
                                        countrySelect.options[i].value.toLowerCase() === country.toLowerCase()) {
                                        countrySelect.selectedIndex = i;
                                        countrySelect.dispatchEvent(new Event('change'));

                                        setTimeout(() => {
                                            if (city && citySelect) {
                                                for (let j = 0; j < citySelect.options.length; j++) {
                                                    if (citySelect.options[j].text.toLowerCase() === city.toLowerCase() ||
                                                        citySelect.options[j].value.toLowerCase() === city.toLowerCase()) {
                                                        citySelect.selectedIndex = j;
                                                        break;
                                                    }
                                                }
                                            }
                                        }, 100);
                                        break;
                                    }
                                }
                            }
                        }
                    })
                    .catch(err => console.error("Geocoding error:", err))
                    .finally(() => {
                         btn.disabled = false;
                         btn.innerHTML = originalText;
                    });

            }, function(err) {
                alert(translations.geoError);
                btn.disabled = false;
                btn.innerHTML = originalText;
            });
        } else {
            alert("Geolocation is not supported by this browser.");
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }

    const geoBtn = document.getElementById('btn-geolocate');
    if (geoBtn) {
        geoBtn.addEventListener('click', getGeoLocation);
    }

    // --- Tab System ---
    function switchTab(type) {
        const activeClass = "flex-1 py-2.5 px-4 rounded-lg text-sm font-semibold bg-white text-red-700 shadow-sm transition-all";
        const inactiveClass = "flex-1 py-2.5 px-4 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-all";

        const tabPerson = document.getElementById('tab-person');
        const tabAnimal = document.getElementById('tab-animal');

        if (tabPerson) tabPerson.className = type === 'person' ? activeClass : inactiveClass;
        if (tabAnimal) tabAnimal.className = type === 'animal' ? activeClass : inactiveClass;

        const blockPersonType = document.getElementById('block-person-type');
        const blockAnimalType = document.getElementById('block-animal-type');
        const blockBreed = document.getElementById('block-breed');
        const blockLastName = document.getElementById('block-last-name');
        const blockAge = document.getElementById('block-age');
        const blockObjects = document.getElementById('block-objects');
        const blockCircumstances = document.getElementById('block-circumstances');

        const sexMale = document.getElementById('sex_option_male');
        const sexFemale = document.getElementById('sex_option_female');

        const labelFirstName = document.getElementById('label-first-name');
        const labelClothing = document.getElementById('label-clothing');
        const inputLastName = document.getElementById('input-last-name');
        const personTypeInput = document.getElementById('person_type_input');
        const personTypeSelect = document.getElementById('person_type_select');

        if (type === 'animal') {
            if(blockPersonType) blockPersonType.style.display = 'none';
            if(blockAnimalType) blockAnimalType.style.display = 'block';
            if(blockBreed) blockBreed.style.display = 'block';
            if(blockLastName) blockLastName.style.display = 'none';
            if(blockAge) blockAge.style.display = 'none';
            if(blockObjects) blockObjects.style.display = 'none';
            if(blockCircumstances) blockCircumstances.style.display = 'none';

            if(inputLastName) inputLastName.required = false;
            if(personTypeInput) personTypeInput.value = 'animal';

            if(labelFirstName) labelFirstName.textContent = translations.animalName;
            if(labelClothing) labelClothing.textContent = translations.animalClothing;

            if(sexMale) sexMale.textContent = translations.maleAnimal;
            if(sexFemale) sexFemale.textContent = translations.femaleAnimal;

        } else {
             if(blockPersonType) blockPersonType.style.display = 'block';
             if(blockAnimalType) blockAnimalType.style.display = 'none';
             if(blockBreed) blockBreed.style.display = 'none';
             if(blockLastName) blockLastName.style.display = 'block';
             if(blockAge) blockAge.style.display = 'block';
             if(blockObjects) blockObjects.style.display = 'block';
             if(blockCircumstances) blockCircumstances.style.display = 'block';

             if(inputLastName) inputLastName.required = true;
             if(personTypeInput && personTypeSelect) personTypeInput.value = personTypeSelect.value;

             if(labelFirstName) labelFirstName.textContent = translations.firstName;
             if(labelClothing) labelClothing.textContent = translations.clothing;

             if(sexMale) sexMale.textContent = translations.male;
             if(sexFemale) sexFemale.textContent = translations.female;
        }
    }

    const tabPerson = document.getElementById('tab-person');
    const tabAnimal = document.getElementById('tab-animal');

    if (tabPerson) tabPerson.addEventListener('click', () => switchTab('person'));
    if (tabAnimal) tabAnimal.addEventListener('click', () => switchTab('animal'));

    // Person Type Input Update
    const personTypeSelect = document.getElementById('person_type_select');
    const personTypeInput = document.getElementById('person_type_input');
    if (personTypeSelect && personTypeInput) {
        personTypeSelect.addEventListener('change', function() {
            personTypeInput.value = this.value;
        });
    }

    // Default Date
    const dateInput = document.querySelector('input[name="disappearance_date"]');
    if (dateInput && !dateInput.value) {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        dateInput.value = now.toISOString().slice(0, 16);
    }
});
