Module.register("MMM-NewsScroller", {
	// Default module config
	defaults: {
		updateInterval: 5000, // 3 seconds scroll interval
		apiUrl: "https://v.juhe.cn/toutiao/index", // Changed to HTTPS
		apiKey: "7268a1f3d036719920a9bff93ca6b6b1", // Default API key
		newsType: "guoji", // Default news type
		updateSchedule: [
			{ hour: 5, minute: 0 }, // 5am
			{ hour: 7, minute: 0 }, // 7am
			{ hour: 11, minute: 0 }, // 11am
			{ hour: 12, minute: 0 }, // 12pm
			{ hour: 14, minute: 0 }, // 2pm
			{ hour: 15, minute: 0 }, // 3pm
			{ hour: 17, minute: 0 }, // 5pm
			{ hour: 19, minute: 0 }, // 7pm
			{ hour: 23, minute: 0 }  // 11pm
		],
		maxNewsItems: 10,
		showSourceInfo: true,
		useNodeFetch: true, // Use node_helper to fetch instead of browser fetch
		enableTranslation: false, // Enable or disable translation
		targetLanguage: "en", // Target language for translation
		baiduAppId: "20250407002326273", // Baidu Translate API appId
		baiduSecretKey: "Srd_2lNeita_aL09ML6q" // Baidu Translate API secretKey
	},
	// Override start method
	start: function() {
		Log.info("Starting module: " + this.name);

		this.newsItems = [];
		this.activeItem = 0;
		this.loaded = false;

		// Register with the node_helper
		const currentLanguage = localStorage.getItem("mm_language")
		// currentLanguage === "Zh-cn"
		// currentLanguage === "En-us"

		this.sendSocketNotification("INIT", this.config);

		// Initial news fetch
		this.fetchNews();

		// Set up the periodic updates and scrolling
		this.scheduleNextUpdate();
		this.scheduleScroll();

		// Register with shared interaction controller
		if (window.InteractionController) {
			InteractionController.register(this, {
				getExpandedContent: this.getExpandedContent.bind(this)
			});
		}
	},

	// Define required styles
	getStyles: function() {
		return ["MMM-NewsScroller.css"];
	},

	// Define required scripts
	getScripts: function() {
		return [];
	},

	// Override socket notification received method
	socketNotificationReceived: function(notification, payload) {
		if (notification === "NEWS_RESULT") {
			if (payload && payload.data) {
				this.processNewsData(payload.data);
			} else {
				Log.error("MMM-NewsScroller: Invalid news data received", payload);
		}
		}
	},

	// Process the news data
	processNewsData: function(data) {
		if (data && data.result && data.result.data) {
			this.newsItems = data.result.data.slice(0, this.config.maxNewsItems);
			this.loaded = true;
			this.updateDom(1000);
			Log.info("MMM-NewsScroller: News updated successfully");
		} else {
			Log.error("MMM-NewsScroller: Unexpected API response format", data);
			// Keep using old news if available
		}
	},

	// Schedule the next API update based on the configured times
	scheduleNextUpdate: function() {
		const now = new Date();
		let nextUpdate = null;
		let earliestTime = null;

		// Find the next scheduled update time
		for (let i = 0; i < this.config.updateSchedule.length; i++) {
			const schedule = this.config.updateSchedule[i];

			// Create a new date object for this scheduled time today
			const scheduleTime = new Date();
			scheduleTime.setHours(schedule.hour, schedule.minute, 0, 0);

			// If this scheduled time is in the future, consider it
			if (scheduleTime > now && (nextUpdate === null || scheduleTime < nextUpdate)) {
				nextUpdate = scheduleTime;
			}

			// Keep track of the earliest time for the next day if needed
			if (earliestTime === null || scheduleTime < earliestTime) {
				earliestTime = scheduleTime;
			}
		}

		// If no future updates today, schedule for the earliest time tomorrow
		if (nextUpdate === null) {
			nextUpdate = new Date(earliestTime);
			nextUpdate.setDate(nextUpdate.getDate() + 1);
		}

		const delay = nextUpdate.getTime() - now.getTime();

		// Schedule the update
		setTimeout(() => {
			this.fetchNews();
			this.scheduleNextUpdate();
		}, delay);

		Log.info("MMM-NewsScroller: Next update scheduled for " + nextUpdate.toLocaleString());
	},

	// Set up periodic scrolling of news items
	scheduleScroll: function() {
		setInterval(() => {
			if (this.newsItems.length > 0) {
				this.activeItem = (this.activeItem + 1) % this.newsItems.length;
				this.updateDom(1000); // Smooth transition with 1 second animation
			}
		}, this.config.updateInterval);
	},

	// Override dom generator
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "news-scroller";

		if (!this.loaded) {
			wrapper.innerHTML = "Loading news...";
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		if (this.newsItems.length === 0) {
			wrapper.innerHTML = "No news available.";
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		const newsItem = this.newsItems[this.activeItem];
		const newsWrapper = document.createElement("div");
		newsWrapper.className = "news-item fade-in";

		// Create title element
		const title = document.createElement("div");
		title.className = "news-title bright";
		title.innerHTML = newsItem.title;
		newsWrapper.appendChild(title);

		// Create source info element if configured
		if (this.config.showSourceInfo) {
			const sourceInfo = document.createElement("div");
			sourceInfo.className = "news-source light small";

			// Format the date
			const newsDate = new Date(newsItem.date);
			const dateString = newsDate.toLocaleDateString(config.language, {
				day: "numeric",
				month: "short",
				hour: "2-digit",
				minute: "2-digit"
			});

			sourceInfo.innerHTML = `${newsItem.category} • ${newsItem.author_name || "Unknown"} • ${dateString}`;
			newsWrapper.appendChild(sourceInfo);

		}

		wrapper.appendChild(newsWrapper);

		// Click to expand via shared controller
		wrapper.style.cursor = "pointer";
		wrapper.addEventListener("click", (event) => {
			event.stopPropagation();
			if (window.InteractionController) {
				InteractionController.expand(this);
			}
		});

		return wrapper;
	},

	// Fetch news from the API
	fetchNews: function() {
		Log.info("MMM-NewsScroller: Fetching news...");

		if (this.config.useNodeFetch) {
			// Use node_helper to fetch the data
			this.sendSocketNotification("FETCH_NEWS", {
				url: this.config.apiUrl,
				key: this.config.apiKey,
				type: this.config.newsType
			});
		} else {
			// Use browser fetch (may have CORS issues)
			const url = `${this.config.apiUrl}?key=${this.config.apiKey}&type=${this.config.newsType}`;

			fetch(url)
				.then(response => response.json())
				.then(data => {
					this.processNewsData(data);
				})
				.catch(error => {
					Log.error("MMM-NewsScroller: Error fetching news", error);
					// Keep using old news if available
				});
		}
		},

		/**
		 * Build expanded news list for the shared interaction card.
		 */
		getExpandedContent: function () {
			var container = document.createElement("div");
			container.className = "news-expanded-container";

			var header = document.createElement("div");
			header.className = "news-expanded-header";
			header.textContent = "📰 Latest News";
			container.appendChild(header);

			if (!this.newsItems || this.newsItems.length === 0) {
				var emptyMsg = document.createElement("div");
				emptyMsg.className = "news-expanded-empty";
				emptyMsg.textContent = "No news available.";
				container.appendChild(emptyMsg);
				return container;
			}

			this.newsItems.forEach(function (item) {
				var newsCard = document.createElement("div");
				newsCard.className = "news-expanded-item";

				var titleEl = document.createElement("div");
				titleEl.className = "news-expanded-title";
				titleEl.textContent = item.title;
				newsCard.appendChild(titleEl);

				var sourceEl = document.createElement("div");
				sourceEl.className = "news-expanded-source";
				var newsDate = new Date(item.date);
				var dateString = newsDate.toLocaleDateString(config.language, {
					day: "numeric", month: "short",
					hour: "2-digit", minute: "2-digit"
				});
				sourceEl.textContent = (item.category || "") + " • " + (item.author_name || "Unknown") + " • " + dateString;
				newsCard.appendChild(sourceEl);

				container.appendChild(newsCard);
			});

			return container;
		},

		notificationReceived: function (notification, payload, sender) {
			if (notification === "LANGUAGE_CHANGED") {
				this.updateDom(0);
			}
		}
	});
