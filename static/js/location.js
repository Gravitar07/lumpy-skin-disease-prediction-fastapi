// Location handling
document.addEventListener('DOMContentLoaded', function() {
    const getLocationBtn = document.getElementById('get-location');
    const locationStatus = document.getElementById('location-status');
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');
    const weatherStatus = document.getElementById('weather-status');
    const toggleWeatherFieldsBtn = document.getElementById('toggle-weather-fields');
    const weatherFieldsContainer = document.getElementById('weather-fields');
    const weatherSummary = document.getElementById('weather-summary');
    
    // Weather display elements
    const cloudCoverDisplay = document.getElementById('cloud-cover-display');
    const meanTempDisplay = document.getElementById('mean-temp-display');
    const minMaxTempDisplay = document.getElementById('min-max-temp-display');
    const precipitationDisplay = document.getElementById('precipitation-display');
    const evapotranspirationDisplay = document.getElementById('evapotranspiration-display');
    const otherValuesDisplay = document.getElementById('other-values-display');
    
    // Temperature and weather input fields
    const minTempInput = document.getElementById('min_temp');
    const meanTempInput = document.getElementById('mean_temp');
    const maxTempInput = document.getElementById('max_temp');
    const cloudCoverInput = document.getElementById('cloud_cover');
    const precipitationInput = document.getElementById('precipitation');
    const evapotranspirationInput = document.getElementById('evapotranspiration');
    const vapourPressureInput = document.getElementById('vapour_pressure');
    const wetDayFreqInput = document.getElementById('wet_day_freq');
    
    // Keep track of weather data status
    let weatherDataFetched = false;
    
    // Toggle weather fields visibility
    toggleWeatherFieldsBtn.addEventListener('click', function() {
        if (weatherFieldsContainer.style.display === 'none') {
            weatherFieldsContainer.style.display = 'block';
            toggleWeatherFieldsBtn.innerHTML = '<i class="bi bi-eye-slash"></i> Hide Weather Fields';
        } else {
            weatherFieldsContainer.style.display = 'none';
            toggleWeatherFieldsBtn.innerHTML = '<i class="bi bi-pencil"></i> Edit Weather Data';
        }
    });
    
    // Weather API key - this comes from the template where it was injected from the server
    // If WEATHER_API_KEY is not defined, provide a fallback for development/testing
    const apiKey = typeof WEATHER_API_KEY !== 'undefined' ? WEATHER_API_KEY : '';
    
    if (!apiKey) {
        console.warn('Weather API key is not available. Weather data will not be loaded.');
        weatherStatus.textContent = 'Weather API key not available. Please enter data manually.';
        weatherFieldsContainer.style.display = 'block'; // Show fields if API key is not available
        toggleWeatherFieldsBtn.style.display = 'none';  // Hide toggle button
    }
    
    getLocationBtn.addEventListener('click', function() {
        if (navigator.geolocation) {
            locationStatus.textContent = 'Getting location...';
            // Hide the summary while fetching new data
            weatherSummary.style.display = 'none';
            
            navigator.geolocation.getCurrentPosition(
                // Success callback
                function(position) {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    
                    // Update location inputs
                    latitudeInput.value = latitude;
                    longitudeInput.value = longitude;
                    
                    locationStatus.textContent = 'Location captured successfully!';
                    locationStatus.className = 'text-success';
                    
                    weatherStatus.textContent = 'Fetching weather data...';
                    
                    // Fetch weather data if API key is available
                    if (apiKey) {
                        fetchWeatherData(latitude, longitude);
                    } else {
                        weatherStatus.textContent = 'Weather API not available. Please enter data manually.';
                        weatherFieldsContainer.style.display = 'block'; // Show fields
                    }
                },
                // Error callback
                function(error) {
                    console.error('Error getting location:', error);
                    locationStatus.textContent = 'Failed to get location. Please try again.';
                    locationStatus.className = 'text-danger';
                    weatherStatus.textContent = 'Location not available. Please enter data manually.';
                    weatherFieldsContainer.style.display = 'block'; // Show fields
                },
                // Options
                {
                    enableHighAccuracy: true,
                    timeout: 5000,
                    maximumAge: 0
                }
            );
        } else {
            locationStatus.textContent = 'Geolocation is not supported by this browser.';
            locationStatus.className = 'text-danger';
            weatherStatus.textContent = 'Geolocation not supported. Please enter data manually.';
            weatherFieldsContainer.style.display = 'block'; // Show fields
        }
    });
    
    // Function to update the weather summary display
    function updateWeatherSummary() {
        // Update the summary display fields
        cloudCoverDisplay.textContent = cloudCoverInput.value + '%';
        meanTempDisplay.textContent = meanTempInput.value + '°C';
        minMaxTempDisplay.textContent = minTempInput.value + '°C / ' + maxTempInput.value + '°C';
        precipitationDisplay.textContent = precipitationInput.value + 'mm';
        evapotranspirationDisplay.textContent = evapotranspirationInput.value + 'mm';
        otherValuesDisplay.textContent = 'VP: ' + vapourPressureInput.value + ', WDF: ' + wetDayFreqInput.value;
        
        // Show the summary
        weatherSummary.style.display = 'block';
    }
    
    // Function to fetch weather data
    function fetchWeatherData(lat, lon) {
        // API endpoint for current weather
        const currentWeatherUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`;
        
        // API endpoint for 5-day forecast (to get min/max temperatures)
        const forecastUrl = `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`;
        
        // First get current weather for mean temperature and cloud cover
        fetch(currentWeatherUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Weather API error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Current weather data:', data);
                
                // Set mean temperature from current weather
                if (data && data.main && data.main.temp) {
                    meanTempInput.value = data.main.temp.toFixed(2);
                }
                
                // Set cloud cover (in percentage)
                if (data && data.clouds && typeof data.clouds.all !== 'undefined') {
                    cloudCoverInput.value = data.clouds.all;
                }
                
                // Set precipitation if available (rain in last 3 hours)
                if (data && data.rain && data.rain['3h']) {
                    precipitationInput.value = data.rain['3h'].toFixed(2);
                } else {
                    // If no rain data, default to 0
                    precipitationInput.value = '0.00';
                }
                
                // Estimate vapor pressure from humidity and temperature
                if (data && data.main && data.main.humidity && data.main.temp) {
                    // Simple approximation for vapor pressure (hPa) based on humidity and temperature
                    const humidity = data.main.humidity; // in %
                    const temperature = data.main.temp; // in Celsius
                    
                    // Saturation vapor pressure (hPa) using Magnus formula
                    const satVaporPressure = 6.112 * Math.exp((17.67 * temperature) / (temperature + 243.5));
                    
                    // Actual vapor pressure (hPa)
                    const vaporPressure = (humidity / 100) * satVaporPressure;
                    
                    vapourPressureInput.value = vaporPressure.toFixed(2);
                }
                
                // Now get forecast data for min/max
                return fetch(forecastUrl);
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Forecast API error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Forecast data:', data);
                
                if (data && data.list && data.list.length > 0) {
                    // Extract min and max temperatures from the forecast
                    let minTemp = 100; // Start with a high value
                    let maxTemp = -100; // Start with a low value
                    let rainDays = 0; // Count days with rain
                    
                    // Check the next 5 days (40 readings for 3-hour intervals)
                    const readings = data.list.slice(0, 40);
                    
                    // Group readings by day to count wet days
                    const dailyRainCheck = {};
                    
                    readings.forEach(reading => {
                        if (reading.main) {
                            if (reading.main.temp_min < minTemp) {
                                minTemp = reading.main.temp_min;
                            }
                            if (reading.main.temp_max > maxTemp) {
                                maxTemp = reading.main.temp_max;
                            }
                            
                            // Check for rainfall to count wet days
                            const date = reading.dt_txt.split(' ')[0]; // Get just the date
                            if (!dailyRainCheck[date]) {
                                dailyRainCheck[date] = false;
                            }
                            
                            // If there's rain in this 3-hour period, mark the day as wet
                            if (reading.rain && reading.rain['3h'] > 0) {
                                dailyRainCheck[date] = true;
                            }
                        }
                    });
                    
                    // Count wet days
                    rainDays = Object.values(dailyRainCheck).filter(isWet => isWet).length;
                    
                    // Update the input fields
                    minTempInput.value = minTemp.toFixed(2);
                    maxTempInput.value = maxTemp.toFixed(2);
                    
                    // Estimate wet day frequency based on forecast
                    // This is days with rain / total days in forecast
                    const daysInForecast = Object.keys(dailyRainCheck).length;
                    if (daysInForecast > 0) {
                        wetDayFreqInput.value = (rainDays / daysInForecast * 30).toFixed(2); // Scale to monthly
                    }
                    
                    // Estimate evapotranspiration based on temperature and other factors
                    // This is a simplified version of the Hargreaves equation
                    const meanTemp = (minTemp + maxTemp) / 2;
                    const tempRange = maxTemp - minTemp;
                    const extraterrestrialRadiation = 15; // Approximate value, varies by latitude and time of year
                    
                    // Simplified Hargreaves formula for reference evapotranspiration (mm/day)
                    const eto = 0.0023 * extraterrestrialRadiation * Math.sqrt(tempRange) * (meanTemp + 17.8);
                    
                    // Set monthly value (approx. 30 days)
                    evapotranspirationInput.value = (eto * 30).toFixed(2);
                }
                
                // Update the weather summary display
                updateWeatherSummary();
                
                // Update status to show all data was loaded
                weatherStatus.innerHTML = `<span class="text-success">✓ Weather data loaded successfully!</span>`;
                weatherDataFetched = true;
            })
            .catch(error => {
                console.error('Error fetching weather data:', error);
                weatherStatus.textContent = 'Error fetching weather data. Please enter values manually.';
                weatherFieldsContainer.style.display = 'block'; // Show fields if API fails
            });
    }
}); 