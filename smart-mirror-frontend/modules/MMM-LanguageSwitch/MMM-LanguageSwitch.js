Module.register("MMM-LanguageSwitch", {
	// Default module config
	defaults: {
		language: "En-us",
	},

	getStyles() {
		return ["MMM-LanguageSwitch.css"];
	},

	// Override start method
	start: function() {
		// Try to get saved language from localStorage, fallback to config
		const savedLanguage = localStorage.getItem("mm_language");
		this.currentLanguage = savedLanguage || this.config.language || "En-us";

		// If we loaded from localStorage and it's different from config, update global config
		if (savedLanguage && config.language !== savedLanguage) {
			config.language = savedLanguage;
		}

		Log.info("Starting module: " + this.name + " with language: " + this.currentLanguage);

		// Register with shared interaction controller for language list expansion
		if (window.InteractionController) {
			InteractionController.register(this, {
				getExpandedContent: this.getExpandedContent.bind(this)
			});
		}
	},

	// Override getDom method
	getDom: function() {
		var wrapper = document.createElement("div");

		// Create language toggle button
		var langButton = document.createElement("button");
		langButton.innerHTML = this.currentLanguage === "En-us" ? "中文" : "English";
		langButton.className = "language-toggle-btn";

		var self = this;

		// Use shared controller for tap (toggle) vs long-press (language list)
		if (window.InteractionController) {
			InteractionController.addTapOrHoldListeners(langButton, {
				onTap: function () {
					self.toggleLanguage();
					langButton.classList.add('pulse');
					setTimeout(function () { langButton.classList.remove('pulse'); }, 600);
				},
				onLongPress: function () {
					InteractionController.expand(self);
				},
				thresholdMs: 500
			});
		} else {
			// Fallback: simple click toggle
			langButton.addEventListener("click", function () {
				self.toggleLanguage();
				langButton.classList.add('pulse');
				setTimeout(function () { langButton.classList.remove('pulse'); }, 600);
			});
		}

		wrapper.appendChild(langButton);

		return wrapper;
	},

	// Add method to toggle language
	toggleLanguage: function() {
		// Toggle between "En-us" and "Zh-cn"
		this.currentLanguage = this.currentLanguage === "En-us" ? "Zh-cn" : "En-us";

		// Save to localStorage for persistence
		localStorage.setItem("mm_language", this.currentLanguage);

		// Use shared controller for soft language switch (no page reload)
		if (window.InteractionController) {
			InteractionController.changeLanguage(this.currentLanguage);
		} else {
			// Fallback: hard reload
			config.language = this.currentLanguage;
			window.location.reload();
		}
	},

	/**
	 * Build language list for the shared interaction card.
	 */
	getExpandedContent: function () {
		var container = document.createElement("div");
		container.className = "language-list-container";

		var title = document.createElement("div");
		title.className = "language-list-title";
		title.textContent = "Select Language / 选择语言";
		container.appendChild(title);

		var languages = [
			{ code: "En-us", label: "English" },
			{ code: "Zh-cn", label: "中文" }
		];

		var self = this;
		languages.forEach(function (lang) {
			var item = document.createElement("div");
			item.className = "language-list-item";
			if (lang.code === self.currentLanguage) {
				item.classList.add("language-list-item--active");
			}
			item.textContent = lang.label;
			item.addEventListener("click", function (e) {
				e.stopPropagation();
				if (lang.code !== self.currentLanguage) {
					self.currentLanguage = lang.code;
					localStorage.setItem("mm_language", self.currentLanguage);
					if (window.InteractionController) {
						InteractionController.dismiss();
						setTimeout(function () {
							InteractionController.changeLanguage(self.currentLanguage);
						}, 300);
					}
				} else {
					if (window.InteractionController) {
						InteractionController.dismiss();
					}
				}
			});
			container.appendChild(item);
		});

		return container;
	},

	notificationReceived: function (notification, payload, sender) {
		if (notification === "LANGUAGE_CHANGED") {
			this.currentLanguage = payload.language;
			this.updateDom(0);
		}
	}
});