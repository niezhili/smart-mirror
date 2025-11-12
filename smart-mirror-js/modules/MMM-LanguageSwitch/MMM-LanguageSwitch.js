Module.register("MMM-LanguageSwitch", {
	defaults: {
		language: "En-us",
	},

	getStyles() {
		return ["MMM-LanguageSwitch.css"];
	},

	start: function () {
		const savedLanguage = localStorage.getItem("mm_language");
		this.currentLanguage = savedLanguage || this.config.language || "En-us";

		if (savedLanguage && config.language !== savedLanguage) {
			config.language = savedLanguage;
		}

		Log.info(
			"Starting module: " + this.name + " with language: " + this.currentLanguage
		);
	},

	getDom: function () {
		var wrapper = document.createElement("div");

		var langButton = document.createElement("button");
		langButton.innerHTML =
			this.currentLanguage === "En-us" ? "中文" : "English";
		langButton.className = "language-toggle-btn";
		langButton.addEventListener("click", () => {
			this.toggleLanguage();
			langButton.classList.add("pulse");
			setTimeout(() => langButton.classList.remove("pulse"), 600);
		});
		wrapper.appendChild(langButton);

		return wrapper;
	},

	toggleLanguage: function () {
		this.currentLanguage =
			this.currentLanguage === "En-us" ? "Zh-cn" : "En-us";

		// 存储
		localStorage.setItem("mm_language", this.currentLanguage);
		config.language = this.currentLanguage;

		console.log("Language changed to: " + config.language);

		// 发送全局通知
		this.sendNotification("LANGUAGE_CHANGED", this.currentLanguage);

		// 更新自己
		this.updateDom();
	},

	notificationReceived: function (notification, payload, sender) {
		if (notification === "LANGUAGE_CHANGED") {
			// 别的模块如果用到语言，可以在这里响应
			console.log(
				this.name + " 收到语言切换: " + payload
			);
			// 如果本模块 UI 需要更新，就调用 this.updateDom()
		}
	},
});
