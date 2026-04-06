Module.register("MMM-Weather", {
	defaults: {
		height: "370px",
		width: "210px",
		updateInterval: 10 * 60 * 1000,
		retryDelay: 2500,
		apiKey: "",
		city: "Hangzhou",
		useAnimations: true,
		showWindDirection: true,
		units: "metric",
		showHumidity: true,
		showWindSpeed: true
	},

	weatherIcons: {
		clear: "SUN",
		sunny: "SUN",
		cloud: "CLOUD",
		overcast: "CLOUD",
		rain: "RAIN",
		drizzle: "RAIN",
		thunder: "STORM",
		snow: "SNOW",
		fog: "FOG",
		haze: "FOG",
		wind: "WIND"
	},

	getTranslations: function () {
		return {
			en: "translations/en.json",
			"zh-cn": "translations/zh-cn.json"
		};
	},

	start: function () {
		Log.info(`Starting module: ${this.name}`);
		this.loaded = false;
		this.errorMessageKey = "";
		this.weatherData = null;
		this.fallbackData = {
			now: {
				text: "WEATHER_UNAVAILABLE",
				temp: "--",
				humidity: "--",
				windSpeed: "--",
				windDir: "--"
			}
		};
		this.scheduleUpdate();
	},

	getStyles: function () {
		return ["MMM-Weather.css"];
	},

	scheduleUpdate: function () {
		clearInterval(this.refreshInterval);
		this.refreshInterval = setInterval(() => {
			this.updateWeather();
		}, this.config.updateInterval);
		this.updateWeather();
	},

	updateWeather: function () {
		this.sendSocketNotification("GET_LOCATION");
	},

	getRequestCoordinates: function () {
		return {
			city: this.config.city || "Hangzhou",
			lat: 30.2741,
			long: 120.1552
		};
	},

	socketNotificationReceived: function (notification, payload) {
		switch (notification) {
			case "LOCATION_RESULT": {
				const coords = this.getRequestCoordinates(payload);
				this.config.city = coords.city;
				const url = `https://api.qweather.com/v7/weather/now?location=${coords.long},${coords.lat}&key=${this.config.apiKey}`;
				this.sendSocketNotification("FETCH_DATA", { url });
				break;
			}
			case "DATA_FETCHED":
				this.errorMessageKey = "";
				this.weatherData = payload;
				this.loaded = true;
				this.updateDom(300);
				break;
			case "LOCATION_ERROR":
				this.handleFailure("LOCATION_UNAVAILABLE");
				break;
			case "FETCH_ERROR":
				this.handleFailure("WEATHER_UNAVAILABLE");
				break;
		}
	},

	handleFailure: function (message) {
		// 接口失败时保留卡片结构，避免整个区域空白。
		this.errorMessageKey = message;
		this.weatherData = this.weatherData || this.fallbackData;
		this.loaded = true;
		this.updateDom(300);
		clearTimeout(this.retryTimer);
		this.retryTimer = setTimeout(() => {
			this.updateWeather();
		}, this.config.retryDelay);
	},

	resolveIcon: function (condition) {
		const normalized = String(condition || "").toLowerCase();
		if (normalized.includes("rain")) return this.weatherIcons.rain;
		if (normalized.includes("snow")) return this.weatherIcons.snow;
		if (normalized.includes("thunder")) return this.weatherIcons.thunder;
		if (normalized.includes("fog") || normalized.includes("haze")) return this.weatherIcons.fog;
		if (normalized.includes("wind")) return this.weatherIcons.wind;
		if (normalized.includes("cloud") || normalized.includes("overcast")) return this.weatherIcons.cloud;
		if (normalized.includes("clear") || normalized.includes("sunny")) return this.weatherIcons.clear;
		return "SKY";
	},

	formatTemperature: function (temp) {
		const tempNum = parseInt(temp, 10);
		let colorClass = "normal-temp";

		if (!Number.isNaN(tempNum)) {
			if (tempNum <= 0) colorClass = "freezing-temp";
			else if (tempNum < 10) colorClass = "cold-temp";
			else if (tempNum > 30) colorClass = "hot-temp";
			else if (tempNum > 25) colorClass = "warm-temp";
		}

		return `<span class="${colorClass}">${temp}${this.config.units === "imperial" ? "F" : "C"}</span>`;
	},

	getSafeWeatherData: function () {
		return this.weatherData && this.weatherData.now ? this.weatherData : this.fallbackData;
	},

	getDom: function () {
		const wrapper = document.createElement("div");
		wrapper.className = "weather-container";

		if (!this.loaded) {
			const loadingDiv = document.createElement("div");
			loadingDiv.className = "weather-loading";
			loadingDiv.textContent = this.translate("LOADING", "Loading weather...");
			wrapper.appendChild(loadingDiv);
			return wrapper;
		}

		const safeData = this.getSafeWeatherData();
		const now = safeData.now || this.fallbackData.now;

		const cityDiv = document.createElement("div");
		cityDiv.className = "weather-city";
		cityDiv.textContent = this.translate(this.config.city || "Hangzhou", this.config.city || "Hangzhou");
		wrapper.appendChild(cityDiv);

		const conditionsDiv = document.createElement("div");
		conditionsDiv.className = "weather-current";

		const mainWeatherDiv = document.createElement("div");
		mainWeatherDiv.className = "weather-main";
		mainWeatherDiv.innerHTML = `
			<div class="weather-emoji ${this.config.useAnimations ? "weather-animated" : ""}">${this.resolveIcon(now.text)}</div>
			<div class="weather-temp">${this.formatTemperature(now.temp || "--")}</div>
		`;
		conditionsDiv.appendChild(mainWeatherDiv);

		const descriptionDiv = document.createElement("div");
		descriptionDiv.className = "weather-description";
		descriptionDiv.textContent = this.translate(now.text || "WEATHER_UNAVAILABLE", now.text || "Weather unavailable");
		conditionsDiv.appendChild(descriptionDiv);
		wrapper.appendChild(conditionsDiv);

		const detailsDiv = document.createElement("div");
		detailsDiv.className = "weather-details";

		if (this.config.showHumidity) {
			const humidityDiv = document.createElement("div");
			humidityDiv.className = "weather-detail";
			humidityDiv.textContent = `${this.translate("HUMIDITY", "Humidity")}: ${now.humidity || "--"}%`;
			detailsDiv.appendChild(humidityDiv);
		}

		if (this.config.showWindSpeed) {
			const windSpeedDiv = document.createElement("div");
			windSpeedDiv.className = "weather-detail weather-wind-speed";
			windSpeedDiv.textContent = `${this.translate("WIND_SPEED", "Wind")}: ${now.windSpeed || "--"} km/h`;
			detailsDiv.appendChild(windSpeedDiv);

			if (this.config.showWindDirection) {
				const windDirDiv = document.createElement("div");
				windDirDiv.className = "weather-detail weather-wind-direction";
				windDirDiv.textContent = now.windDir || "--";
				detailsDiv.appendChild(windDirDiv);
			}
		}

		const updateDiv = document.createElement("div");
		updateDiv.className = "weather-updated";
		updateDiv.textContent = this.errorMessageKey
			? this.translate(this.errorMessageKey, this.errorMessageKey)
			: `${this.translate("UPDATED", "Updated")}: ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
		detailsDiv.appendChild(updateDiv);

		wrapper.appendChild(detailsDiv);
		return wrapper;
	},

	stop: function () {
		clearInterval(this.refreshInterval);
		clearTimeout(this.retryTimer);
	}
});

