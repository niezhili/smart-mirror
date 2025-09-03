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
	},

	// Override getDom method
	getDom: function() {
		var wrapper = document.createElement("div");

		// Create language toggle button
		var langButton = document.createElement("button");
		langButton.innerHTML = this.currentLanguage === "En-us" ? "中文" : "English";
		langButton.className = "language-toggle-btn";
		langButton.addEventListener("click", () => {
			this.toggleLanguage();
			langButton.classList.add('pulse');
			setTimeout(() => langButton.classList.remove('pulse'), 600);
		});
		wrapper.appendChild(langButton);

		return wrapper;
	},

	// Add method to toggle language
	toggleLanguage: function() {
		// Toggle between "en" and "cn"
		this.currentLanguage = this.currentLanguage === "En-us" ? "Zh-cn" : "En-us";

		// Save to localStorage for persistence
		localStorage.setItem("mm_language", this.currentLanguage);

		// Update the config
		config.language = this.currentLanguage;

		// Log for debugging
		console.log("Language changed to: " + config.language);

		// Force a complete page reload to apply changes
		window.location.reload();
	}
});
