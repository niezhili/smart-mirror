Module.register("MMM-Weather", {
	defaults: {
		height: "370px",
		width: "210px",
		timeZone: "c78", // China by default
		updateInterval: 10 * 60 * 1000, // 10 minutes
		retryDelay: 2500,
		apiKey: "", // Will be set from config
		city: "",
		useAnimations: true, // Enable animations
		showWindDirection: true,
		units: "metric", // celsius by default
		showHumidity: true,
		showWindSpeed: true,
		currentLanguage: ""
	},

	// Weather condition to emoji mapping
	weatherEmojis: {
		"Clear": "鈽€锔?,
		"Sunny": "鈽€锔?,
		"Mostly Clear": "馃尋锔?,
		"Mostly Sunny": "馃尋锔?,
		"Partly Cloudy": "鉀?,
		"Cloudy": "鈽侊笍",
		"Overcast": "鈽侊笍",
		"Foggy": "馃尗锔?,
		"Haze": "馃尗锔?,
		"Light Rain": "馃對锔?,
		"Moderate Rain": "馃導锔?,
		"Heavy Rain": "馃導锔?,
		"Drizzle": "馃對锔?,
		"Thunderstorm": "鉀堬笍",
		"Thundershowers": "鉀堬笍",
		"Snow": "鉂勶笍",
		"Light Snow": "馃尐锔?,
		"Moderate Snow": "鉂勶笍",
		"Heavy Snow": "鉂勶笍",
		"Sleet": "馃尐锔?,
		"Dust": "馃挩",
		"Sand": "馃挩",
		"Wind": "馃挩"
	},

	// Wind direction to arrow emoji mapping
	windDirections: {
		"N": "猬嗭笍",
		"NNE": "鈫楋笍",
		"NE": "鈫楋笍",
		"ENE": "鈫楋笍",
		"E": "鉃★笍",
		"ESE": "鈫橈笍",
		"SE": "鈫橈笍",
		"SSE": "鈫橈笍",
		"S": "猬囷笍",
		"SSW": "鈫欙笍",
		"SW": "鈫欙笍",
		"WSW": "鈫欙笍",
		"W": "猬咃笍",
		"WNW": "鈫栵笍",
		"NW": "鈫栵笍",
		"NNW": "鈫栵笍"
	},

	start: function () {
		this.currentLanguage = config.language;
		// console.log("Current language: ",this.currentLanguage);
		Log.info("Starting module: " + this.name);
		this.loaded = false;
		this.weatherData = null;
		this.scheduleUpdate();
	},

	getTranslations: function () {
		// const language = config.language.toLowerCase(); // Ensure case-insensitivity
		const savedLanguage = localStorage.getItem("mm_language");

		if(savedLanguage === "En-us"){
			return {en: "translations/en.json"}
		}else if(savedLanguage === "Zh-cn"){
			return {cn: "translations/cn.json"}
		}
	},

	getStyles: function () {
		return ["MMM-Weather.css"];
	},

	scheduleUpdate: function () {
		const self = this;
		setInterval(() => {
			self.updateWeather();
		}, this.config.updateInterval);
		self.updateWeather();
	},

	updateWeather: function () {
		this.sendSocketNotification("GET_LOCATION");
	},

	socketNotificationReceived: function (notification, payload) {
		switch (notification) {
			case "LOCATION_RESULT":
				// this.config.city = payload.city;
				this.config.city = "Hangzhou";
				this.config.lat = 30.2741;
				this.config.long =120.1552 ;

				// const url = `https://api.qweather.com/v7/weather/now?location=${payload.long},${payload.lat}&key=${this.config.apiKey}`;
				const url = `https://api.qweather.com/v7/weather/now?location=${this.config.long},${this.config.lat}&key=${this.config.apiKey}`;
				console.log("[MMM-CustomizedWeather] Requesting weather from:", url);
				this.sendSocketNotification("FETCH_DATA", {url: url});
				break;
			case "DATA_FETCHED":
				this.weatherData = payload;
				this.loaded = true;
				this.updateDom();
				break;
			case "LOCATION_ERROR":
				this.scheduleRetry();
				break;
			case "FETCH_ERROR":
				this.scheduleRetry();
				break;
		}
	},

	scheduleRetry: function () {
		const self = this;
		setTimeout(() => {
			self.updateWeather();
		}, this.config.retryDelay);
	},

	// Get appropriate emoji for weather condition
	getWeatherEmoji: function (condition) {
		return this.weatherEmojis[condition] || "馃寛"; // Default to rainbow if condition not found
	},

	// Get appropriate emoji for wind direction
	getWindDirectionEmoji: function (direction) {
		return this.windDirections[direction] || "馃Л"; // Default to compass if direction not found
	},

	// Format temperature with color based on value
	formatTemperature: function (temp) {
		const tempNum = parseInt(temp);
		let colorClass = "normal-temp";

		if (tempNum <= 0) colorClass = "freezing-temp";
		else if (tempNum < 10) colorClass = "cold-temp";
		else if (tempNum > 30) colorClass = "hot-temp";
		else if (tempNum > 25) colorClass = "warm-temp";

		return `<span class="${colorClass}">${temp}掳${this.config.units === "imperial" ? "F" : "C"}</span>`;
	},

	getDom: function () {
		const wrapper = document.createElement('div');
		wrapper.className = 'weather-container';

		if (!this.loaded) {
			const loadingDiv = document.createElement('div');
			loadingDiv.className = 'weather-loading';
			loadingDiv.innerHTML = '馃攧 ' + this.translate("LOADING");
			wrapper.appendChild(loadingDiv);
			return wrapper;
		}

		if (!this.weatherData || !this.weatherData.now) {
			const errorDiv = document.createElement('div');
			errorDiv.className = 'weather-error';
			errorDiv.innerHTML = '鉂?' + this.translate("NO_DATA");
			wrapper.appendChild(errorDiv);
			return wrapper;
		}

		try {
			// City header with location pin emoji
			const cityDiv = document.createElement('div');
			cityDiv.className = 'weather-city';
			cityDiv.innerHTML = `馃搷 ${this.translate(this.config.city)}`;
			wrapper.appendChild(cityDiv);

			// Current weather conditions with emoji
			const weatherCondition = ["en", "En-us"].includes(config.language.toLowerCase()) ?
				this.translate(this.weatherData.now.text) : this.weatherData.now.text;

			const weatherEmoji = this.getWeatherEmoji(weatherCondition);

			const conditionsDiv = document.createElement('div');
			conditionsDiv.className = 'weather-current';

			// Large emoji and temperature display
			const mainWeatherDiv = document.createElement('div');
			mainWeatherDiv.className = 'weather-main';
			mainWeatherDiv.innerHTML = `
                <div class="weather-emoji ${this.config.useAnimations ? 'weather-animated' : ''}">${weatherEmoji}</div>
                <div class="weather-temp">${this.formatTemperature(this.weatherData.now.temp)}</div>
            `;
			conditionsDiv.appendChild(mainWeatherDiv);

			// Weather description
			const descriptionDiv = document.createElement('div');
			descriptionDiv.className = 'weather-description';
			descriptionDiv.textContent = this.translate(weatherCondition);
			conditionsDiv.appendChild(descriptionDiv);

			wrapper.appendChild(conditionsDiv);

			// Weather details section
			const detailsDiv = document.createElement('div');
			detailsDiv.className = 'weather-details';
			detailsDiv.style.fontSize = '0.6rem';

			// Only show humidity if configured
			if (this.config.showHumidity) {
				const humidityDiv = document.createElement('div');
				humidityDiv.className = 'weather-detail';
				humidityDiv.innerHTML = `馃挧 ${this.translate("HUMIDITY")}: ${this.weatherData.now.humidity}%`;
				detailsDiv.appendChild(humidityDiv);
			}

			// Only show wind if configured
			if (this.config.showWindSpeed) {
				const windSpeedDiv = document.createElement('div');
				windSpeedDiv.className = 'weather-detail weather-wind-speed';
				windSpeedDiv.style.fontSize = "0.6rem";
				windSpeedDiv.innerHTML = `馃挩 ${this.translate("WIND_SPEED")}: ${this.weatherData.now.windSpeed} km/h`;
				detailsDiv.appendChild(windSpeedDiv);

				// Add wind direction if configured
				if (this.config.showWindDirection && this.weatherData.now.windDir) {
					const windDirDiv = document.createElement('div');
					windDirDiv.className = 'weather-detail weather-wind-direction';
					windDirDiv.style.fontSize = "0.6rem";
					const directionEmoji = this.getWindDirectionEmoji(this.weatherData.now.windDir);
					windDirDiv.innerHTML = `${directionEmoji} ${this.translate(this.weatherData.now.windDir)}`;
					detailsDiv.appendChild(windDirDiv);
				}
			}

			// Add last updated info
			const updateDiv = document.createElement('div');
			updateDiv.className = 'weather-updated';
			const updateTime = new Date().toLocaleTimeString([], {hour: 'numeric', minute: '2-digit'});
			updateDiv.textContent = `馃晵 ${this.translate("UPDATED")}: ${updateTime}`;
			detailsDiv.appendChild(updateDiv);

			wrapper.appendChild(detailsDiv);

		} catch (e) {
			console.error("[MMM-Weather] Error rendering weather:", e);
			wrapper.innerHTML = "鉂?" + this.translate("ERROR_DISPLAY");
		}

		return wrapper;
	}
});

