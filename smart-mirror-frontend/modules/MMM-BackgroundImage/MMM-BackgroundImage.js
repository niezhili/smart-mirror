/**
 * @author Marrion Joseph NTADI
 * @github https://github.com/HeadStone7
 */

Module.register("MMM-BackgroundImage", {
	defaults: {
		height: "100vh",
		width: "100vw",
		animationSpeed: "0",
		updateInterval: 60 * 60 * 1000,
	},

	start: function() {
		this.wallpaperUrl = null;
		this.specialDate = null;

		Log.info("MMM-BackgroundImage: start() called, fetching wallpaper...");
		this.getWallpaper();

		// Set interval for periodic updates
		this.interval = setInterval(() => {
			this.getWallpaper();
		}, this.config.updateInterval);
	},

	getWallpaper: function() {
		const dateInfo = this.getCurrentDateInfo();
		Log.info("MMM-BackgroundImage: requesting wallpaper for date:", dateInfo.dateString);
		this.sendSocketNotification("GET_WALLPAPER", {
			dateString: dateInfo.dateString,
			modulePath: this.data.path
		});
	},

	// Receive results from node_helper
	socketNotificationReceived: function(notification, payload) {
		if (notification === "WALLPAPER_URL") {
			Log.info("MMM-BackgroundImage: received WALLPAPER_URL:", payload.url);
			this.wallpaperUrl = payload.url;
			this.updateDom(this.config.animationSpeed);
		}
	},

	getStyles: function() {
		return ["MMM-BackgroundImage.css"];
	},

	getDom: function() {
		const wrapper = document.createElement("div");

		if (this.wallpaperUrl) {
			Log.info("MMM-BackgroundImage: rendering image:", this.wallpaperUrl);
			const image = document.createElement("img");
			image.className = "photo";
			image.src = this.wallpaperUrl;
			image.alt = "Background image";
			wrapper.appendChild(image);
		} else {
			// Show loading state
			wrapper.innerHTML = "Loading background...";
		}

		return wrapper;
	},

	getCurrentDateInfo: function() {
		const now = new Date();
		const month = String(now.getMonth() + 1).padStart(2, '0');
		const day = String(now.getDate()).padStart(2, '0');
		return {
			dateString: `${month}-${day}`
		};
	},

	// Listen for background change requests from other modules
	notificationReceived: function(notification, payload, sender) {
		if (notification === "CHANGE_BACKGROUND") {
			Log.info("MMM-BackgroundImage: changing wallpaper");
			this.getWallpaper();
		}
	},

	// Clean up interval on stop
	stop: function() {
		clearInterval(this.interval);
	}
});
