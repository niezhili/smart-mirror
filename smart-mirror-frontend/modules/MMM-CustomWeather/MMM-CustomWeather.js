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
		"Wind": "💨",
		// Chinese weather conditions (from Juhe API)
		"晴": "☀️",
		"多云": "⛅",
		"阴": "☁️",
		"小雨": "🌦️",
		"中雨": "🌧️",
		"大雨": "🌧️",
		"阵雨": "🌦️",
		"雷阵雨": "⛈️",
		"雷阵雨伴有冰雹": "⛈️",
		"小雪": "🌨️",
		"中雪": "❄️",
		"大雪": "❄️",
		"暴雪": "❄️",
		"雾": "🌫️",
		"霾": "🌫️",
		"大风": "💨",
		"扬沙": "💨",
		"浮尘": "💨",
		"沙尘暴": "💨",
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
		"NNW": "↖️",
		// Chinese wind directions (from Juhe API)
		"北风": "⬆️",
		"东北风": "↗️",
		"东风": "➡️",
		"东南风": "↘️",
		"南风": "⬇️",
		"西南风": "↙️",
		"西风": "⬅️",
		"西北风": "↖️",
	},

	start: function () {
		this.currentLanguage = config.language;
		Log.info("Starting module: " + this.name);
		this.loaded = false;
		this.weatherData = null;
		this.scheduleUpdate();

		// Register with shared interaction controller
		if (window.InteractionController) {
			InteractionController.register(this, {
				getExpandedContent: this.getExpandedContent.bind(this)
			});
		}
	},

	getTranslations: function () {
		const savedLanguage = localStorage.getItem("mm_language");

		if(savedLanguage === "En-us"){
			return {en: "translations/en.json"}
		}else if(savedLanguage === "Zh-cn"){
			return {cn: "translations/cn.json"}
		}
	},

	getStyles: function () {
		return ["MMM-CustomWeather.css"];
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
				this.config.city = "Hangzhou";
				const url = `https://apis.juhe.cn/simpleWeather/query?city=${encodeURIComponent("杭州")}&key=${this.config.apiKey}`;
				this.sendSocketNotification("FETCH_DATA", {url: url});
				break;
			case "DATA_FETCHED":
				if (payload.error_code !== 0) {
					Log.error("[MMM-CustomWeather] API error: " + payload.reason);
					this.scheduleRetry();
					return;
				}
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

	getWeatherEmoji: function (condition) {
		return this.weatherEmojis[condition] || "🌈";
	},

	getWindDirectionEmoji: function (direction) {
		return this.windDirections[direction] || "🧭";
	},

	formatTemperature: function (temp) {
		const tempNum = parseInt(temp);
		let colorClass = "normal-temp";

		if (tempNum <= 0) colorClass = "freezing-temp";
		else if (tempNum < 10) colorClass = "cold-temp";
		else if (tempNum > 30) colorClass = "hot-temp";
		else if (tempNum > 25) colorClass = "warm-temp";

		return `<span class="${colorClass}">${temp}°${this.config.units === "imperial" ? "F" : "C"}</span>`;
	},

	getDom: function () {
		const wrapper = document.createElement('div');
		wrapper.className = 'weather-container';

		if (!this.loaded) {
			const loadingDiv = document.createElement('div');
			loadingDiv.className = 'weather-loading';
			loadingDiv.innerHTML = '🔄 ' + this.translate("LOADING");
			wrapper.appendChild(loadingDiv);
			return wrapper;
		}

		if (!this.weatherData || !this.weatherData.result || !this.weatherData.result.realtime) {
			const errorDiv = document.createElement('div');
			errorDiv.className = 'weather-error';
			errorDiv.innerHTML = '❌ ' + this.translate("NO_DATA");
			wrapper.appendChild(errorDiv);
			return wrapper;
		}

		try {
			// City header
			const cityDiv = document.createElement('div');
			cityDiv.className = 'weather-city';
			cityDiv.innerHTML = `📍 ${this.translate(this.config.city)}`;
			wrapper.appendChild(cityDiv);

			// Current weather conditions
			const weatherCondition = ["en", "En-us"].includes(config.language.toLowerCase()) ?
				this.translate(this.weatherData.result.realtime.info) : this.weatherData.result.realtime.info;

			const weatherEmoji = this.getWeatherEmoji(weatherCondition);

			const conditionsDiv = document.createElement('div');
			conditionsDiv.className = 'weather-current';

			// Large emoji and temperature display
			const mainWeatherDiv = document.createElement('div');
			mainWeatherDiv.className = 'weather-main';
			mainWeatherDiv.innerHTML = `
                <div class="weather-emoji ${this.config.useAnimations ? 'weather-animated' : ''}">${weatherEmoji}</div>
                <div class="weather-temp">${this.formatTemperature(this.weatherData.result.realtime.temperature)}</div>
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

			if (this.config.showHumidity) {
				const humidityDiv = document.createElement('div');
				humidityDiv.className = 'weather-detail';
				humidityDiv.innerHTML = `💧 ${this.translate("HUMIDITY")}: ${this.weatherData.result.realtime.humidity}%`;
				detailsDiv.appendChild(humidityDiv);
			}

			if (this.config.showWindSpeed) {
				const windSpeedDiv = document.createElement('div');
				windSpeedDiv.className = 'weather-detail weather-wind-speed';
				windSpeedDiv.style.fontSize = "0.6rem";
				windSpeedDiv.innerHTML = `💨 ${this.translate("WIND_SPEED")}: ${this.weatherData.result.realtime.power}`;
				detailsDiv.appendChild(windSpeedDiv);

				if (this.config.showWindDirection && this.weatherData.result.realtime.direct) {
					const windDirDiv = document.createElement('div');
					windDirDiv.className = 'weather-detail weather-wind-direction';
					windDirDiv.style.fontSize = "0.6rem";
					const directionEmoji = this.getWindDirectionEmoji(this.weatherData.result.realtime.direct);
					windDirDiv.innerHTML = `${directionEmoji} ${this.translate(this.weatherData.result.realtime.direct)}`;
					detailsDiv.appendChild(windDirDiv);
				}
			}

			// Last updated
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

		// Click handler: expand via shared controller
		wrapper.style.cursor = "pointer";
		wrapper.addEventListener("click", (event) => {
			event.stopPropagation();
			if (window.InteractionController) {
				InteractionController.expand(this);
			}
		});

		return wrapper;
	},

	/**
	 * Build enriched weather content for the expanded card.
	 */
	getExpandedContent: function () {
		const container = document.createElement("div");
		container.className = "weather-expanded-content";

		const weatherCondition = ["en", "En-us"].includes(config.language.toLowerCase()) ?
			this.translate(this.weatherData.result.realtime.info) : this.weatherData.result.realtime.info;
		const weatherEmoji = this.getWeatherEmoji(weatherCondition);

		// City header
		const header = document.createElement("div");
		header.className = "weather-expanded-header";
		header.textContent = `📍 ${this.translate(this.config.city)}`;
		container.appendChild(header);

		// Main row: large emoji + temperature
		const mainRow = document.createElement("div");
		mainRow.className = "weather-expanded-main";

		const emojiEl = document.createElement("div");
		emojiEl.className = "weather-expanded-emoji";
		emojiEl.textContent = weatherEmoji;

		const tempEl = document.createElement("div");
		tempEl.className = "weather-expanded-temp";
		tempEl.innerHTML = this.formatTemperature(this.weatherData.result.realtime.temperature);

		mainRow.appendChild(emojiEl);
		mainRow.appendChild(tempEl);
		container.appendChild(mainRow);

		// Weather description
		const descEl = document.createElement("div");
		descEl.className = "weather-expanded-description";
		descEl.textContent = this.translate(weatherCondition);
		container.appendChild(descEl);

		// Details grid
		const detailsGrid = document.createElement("div");
		detailsGrid.className = "weather-expanded-details";

		// Feels like
		if (this.weatherData.result.realtime.feelsLike !== undefined) {
			detailsGrid.appendChild(this._createDetailItem(
				"🌡️", this.translate("FEELS_LIKE"), `${this.weatherData.result.realtime.temperature}°${this.config.units === "imperial" ? "F" : "C"}`
			));
		}

		// Humidity
		if (this.config.showHumidity) {
			detailsGrid.appendChild(this._createDetailItem(
				"💧", this.translate("HUMIDITY"), `${this.weatherData.result.realtime.humidity}%`
			));
		}

		// Wind
		if (this.config.showWindSpeed) {
			let windText = `${this.weatherData.result.realtime.power}`;
			if (this.config.showWindDirection && this.weatherData.result.realtime.direct) {
				windText += ` ${this.getWindDirectionEmoji(this.weatherData.result.realtime.direct)} ${this.translate(this.weatherData.result.realtime.direct)}`;
			}
			detailsGrid.appendChild(this._createDetailItem(
				"💨", this.translate("WIND_SPEED"), windText
			));
		}

		// Update time
		const updateTime = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
		detailsGrid.appendChild(this._createDetailItem(
			"🕒", this.translate("UPDATED"), updateTime
		));

		container.appendChild(detailsGrid);
		return container;
	},

	/**
	 * Helper: create a detail item row for the expanded view.
	 */
	_createDetailItem: function (emoji, label, value) {
		const item = document.createElement("div");
		item.className = "weather-expanded-detail-item";

		const labelEl = document.createElement("div");
		labelEl.className = "weather-expanded-detail-label";
		labelEl.textContent = `${emoji} ${label}`;

		const valueEl = document.createElement("div");
		valueEl.className = "weather-expanded-detail-value";
		valueEl.textContent = value;

		item.appendChild(labelEl);
		item.appendChild(valueEl);
		return item;
	},

});
