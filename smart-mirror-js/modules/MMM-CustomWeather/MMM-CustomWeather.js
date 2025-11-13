Module.register("MMM-CustomWeather", {
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
		"Clear": "☀️",
		"Sunny": "☀️",
		"Mostly Clear": "🌤️",
		"Mostly Sunny": "🌤️",
		"Partly Cloudy": "⛅",
		"Cloudy": "☁️",
		"Overcast": "☁️",
		"Foggy": "🌫️",
		"Haze": "🌫️",
		"Light Rain": "🌦️",
		"Moderate Rain": "🌧️",
		"Heavy Rain": "🌧️",
		"Drizzle": "🌦️",
		"Thunderstorm": "⛈️",
		"Thundershowers": "⛈️",
		"Snow": "❄️",
		"Light Snow": "🌨️",
		"Moderate Snow": "❄️",
		"Heavy Snow": "❄️",
		"Sleet": "🌨️",
		"Dust": "💨",
		"Sand": "💨",
		"Wind": "💨"
	},

	// Wind direction to arrow emoji mapping
	windDirections: {
		"N": "⬆️",
		"NNE": "↗️",
		"NE": "↗️",
		"ENE": "↗️",
		"E": "➡️",
		"ESE": "↘️",
		"SE": "↘️",
		"SSE": "↘️",
		"S": "⬇️",
		"SSW": "↙️",
		"SW": "↙️",
		"WSW": "↙️",
		"W": "⬅️",
		"WNW": "↖️",
		"NW": "↖️",
		"NNW": "↖️"
	},

	start: async function () {
		this.currentLanguage = this.normalizeLanguage(config.language);
		Log.info("Starting module: " + this.name);
		this.loaded = false;
		this.weatherData = null;
		this.highlighted = false;
		this.highlightOverlay = null;
		this.highlightedElement = null;
		this.boundHandleHighlightKeydown = this.handleHighlightKeydown.bind(this);

		try {
			await this.reloadTranslationsFor(this.currentLanguage);
		} catch (error) {
			Log.error("[MMM-CustomWeather] Failed to initialize translations:", error);
		}

		this.scheduleUpdate();
	},

	getTranslations: function () {
		return {
			en: "translations/en.json",
			"en-us": "translations/en.json",
			"zh-cn": "translations/cn.json",
			zh: "translations/cn.json",
			cn: "translations/cn.json"
		};
	},

	getStyles: function () {
		return ["MMM-CustomWeather.css"];
	},

	normalizeLanguage: function (language) {
		if (!language || typeof language !== "string") {
			return "en";
		}
		const code = language.toLowerCase();

		if (code.startsWith("en")) {
			return "en";
		}

		if (code === "zh-cn" || code === "zh" || code === "cn") {
			return "zh-cn";
		}

		return code;
	},

	isEnglishLanguage: function (language) {
		return this.normalizeLanguage(language).startsWith("en");
	},

	reloadTranslationsFor: async function (language) {
		if (typeof Translator === "undefined") {
			return;
		}

		const normalized = this.normalizeLanguage(language);
		const originalLanguage = config.language;

		if (Translator.translations && Translator.translations[this.name]) {
			delete Translator.translations[this.name];
		}

		if (Translator.translationsFallback && Translator.translationsFallback[this.name]) {
			delete Translator.translationsFallback[this.name];
		}

		config.language = normalized;

		try {
			await this.loadTranslations();
		} finally {
			config.language = originalLanguage;
		}
	},

	createHighlightOverlay: function () {
		if (!this.highlightOverlay) {
			const overlay = document.createElement("div");
			overlay.className = "weather-highlight-overlay";
			overlay.addEventListener("click", () => this.deactivateHighlight());
			this.highlightOverlay = overlay;
		}
		return this.highlightOverlay;
	},

	activateHighlight: function (wrapper) {
		if (!wrapper) {
			return;
		}

		this.highlightedElement = wrapper;

		if (this.highlighted) {
			wrapper.classList.add("weather-highlighted");
			return;
		}

		const overlay = this.createHighlightOverlay();

		if (!overlay.parentNode) {
			document.body.appendChild(overlay);
		}

		document.addEventListener("keydown", this.boundHandleHighlightKeydown, true);

		requestAnimationFrame(() => {
			overlay.classList.add("weather-highlight-overlay--visible");
			wrapper.classList.add("weather-highlighted");
		});

		this.highlighted = true;
	},

	deactivateHighlight: function () {
		if (!this.highlighted) {
			return;
		}

		if (this.highlightedElement) {
			this.highlightedElement.classList.remove("weather-highlighted");
			this.highlightedElement = null;
		}

		if (this.highlightOverlay) {
			this.highlightOverlay.classList.remove("weather-highlight-overlay--visible");
			if (this.highlightOverlay.parentNode) {
				this.highlightOverlay.parentNode.removeChild(this.highlightOverlay);
			}
		}

		document.removeEventListener("keydown", this.boundHandleHighlightKeydown, true);

		this.highlighted = false;
	},

	handleHighlightKeydown: function (event) {
		if (event.key === "Escape") {
			this.deactivateHighlight();
		}
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
		return this.weatherEmojis[condition] || "🌈"; // Default to rainbow if condition not found
	},

	// Get appropriate emoji for wind direction
	getWindDirectionEmoji: function (direction) {
		return this.windDirections[direction] || "🧭"; // Default to compass if direction not found
	},

	// Format temperature with color based on value
	formatTemperature: function (temp) {
		const tempNum = parseInt(temp);
		let colorClass = "normal-temp";

		if (tempNum <= 0) colorClass = "freezing-temp";
		else if (tempNum < 10) colorClass = "cold-temp";
		else if (tempNum > 30) colorClass = "hot-temp";
		else if (tempNum > 25) colorClass = "warm-temp";

		return `<span class="${colorClass}">${temp}°${this.config.units === "imperial" ? "F" : "C"}</span>`;
	},

	// 监听器，响应翻译更新
	notificationReceived: async function (notification, payload) {
		// 监听语言切换通知
		if (notification === "LANGUAGE_CHANGED") {
			const normalized = this.normalizeLanguage(payload);
			Log.info(`[MMM-CustomWeather] 语言切换为: ${payload} (normalized: ${normalized})`);

			if (normalized === this.currentLanguage) {
				return;
			}

			this.currentLanguage = normalized;

			try {
				await this.reloadTranslationsFor(normalized);
			} catch (error) {
				Log.error("[MMM-CustomWeather] Failed to reload translations after language change:", error);
			}

			this.updateDom();
		}
	},

	getDom: function () {
		const wrapper = document.createElement('div');
		wrapper.className = 'weather-container';

		wrapper.addEventListener("click", () => {
			if (this.highlighted || !this.loaded || !this.weatherData) {
				return;
			}
			this.activateHighlight(wrapper);
		});

		if (this.highlighted) {
			this.highlightedElement = wrapper;
			wrapper.classList.add("weather-highlighted");
		}

		if (!this.loaded) {
			const loadingDiv = document.createElement('div');
			loadingDiv.className = 'weather-loading';
			loadingDiv.innerHTML = '🔄 ' + this.translate("LOADING");
			wrapper.appendChild(loadingDiv);
			return wrapper;
		}

		if (!this.weatherData || !this.weatherData.now) {
			const errorDiv = document.createElement('div');
			errorDiv.className = 'weather-error';
			errorDiv.innerHTML = '❌ ' + this.translate("NO_DATA");
			wrapper.appendChild(errorDiv);
			return wrapper;
		}

		try {
			// City header with location pin emoji
			const cityDiv = document.createElement('div');
			cityDiv.className = 'weather-city';
			cityDiv.innerHTML = `📍 ${this.translate(this.config.city)}`;
			wrapper.appendChild(cityDiv);

			// Current weather conditions with emoji
			const weatherCondition = this.isEnglishLanguage(this.currentLanguage) ?
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
				humidityDiv.innerHTML = `💧 ${this.translate("HUMIDITY")}: ${this.weatherData.now.humidity}%`;
				detailsDiv.appendChild(humidityDiv);
			}

			// Only show wind if configured
			if (this.config.showWindSpeed) {
				const windSpeedDiv = document.createElement('div');
				windSpeedDiv.className = 'weather-detail weather-wind-speed';
				windSpeedDiv.style.fontSize = "0.6rem";
				windSpeedDiv.innerHTML = `💨 ${this.translate("WIND_SPEED")}: ${this.weatherData.now.windSpeed} km/h`;
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
			updateDiv.textContent = `🕒 ${this.translate("UPDATED")}: ${updateTime}`;
			detailsDiv.appendChild(updateDiv);

			wrapper.appendChild(detailsDiv);

		} catch (e) {
			console.error("[MMM-CustomWeather] Error rendering weather:", e);
			wrapper.innerHTML = "❌ " + this.translate("ERROR_DISPLAY");
		}

		return wrapper;
	}
});