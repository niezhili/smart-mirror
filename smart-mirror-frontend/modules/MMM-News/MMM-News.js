Module.register("MMM-News", {
	defaults: {
		updateInterval: 5 * 60 * 1000,
		apiUrl: "https://v.juhe.cn/toutiao/index",
		apiKey: "7268a1f3d036719920a9bff93ca6b6b1",
		newsType: "guoji",
		updateSchedule: [
			{ hour: 5, minute: 0 },
			{ hour: 7, minute: 0 },
			{ hour: 11, minute: 0 },
			{ hour: 12, minute: 0 },
			{ hour: 14, minute: 0 },
			{ hour: 15, minute: 0 },
			{ hour: 17, minute: 0 },
			{ hour: 19, minute: 0 },
			{ hour: 23, minute: 0 }
		],
		maxNewsItems: 10,
		panelTitleKey: "PANEL_TITLE",
		panelHeight: 520,
		swipeThreshold: 70,
		categories: [
			{ key: "top", labelKey: "CATEGORY_TOP" },
			{ key: "guonei", labelKey: "CATEGORY_GUONEI" },
			{ key: "tiyu", labelKey: "CATEGORY_TIYU" },
			{ key: "keji", labelKey: "CATEGORY_KEJI" },
			{ key: "guoji", labelKey: "CATEGORY_GUOJI" }
		]
	},

	getTranslations: function () {
		return {
			en: "translations/en.json",
			"zh-cn": "translations/zh-cn.json"
		};
	},

	start: function () {
		Log.info(`Starting module: ${this.name}`);
		this.newsByCategory = {};
		this.loadingCategories = new Set();
		this.activeCategoryIndex = Math.max(0, this.config.categories.findIndex((item) => item.key === this.config.newsType));
		this.pointerStart = null;
		this.fetchAllCategories();
		this.scheduleNextUpdate();
	},

	getStyles: function () {
		return ["MMM-News.css"];
	},

	socketNotificationReceived: function (notification, payload) {
		if (notification !== "NEWS_RESULT" || !payload || !payload.type) {
			return;
		}

		this.loadingCategories.delete(payload.type);
		if (payload.error) {
			Log.error(`MMM-News: ${payload.type} failed`, payload.error);
			return;
		}

		this.processNewsData(payload.type, payload.data);
	},

	processNewsData: function (categoryKey, data) {
		if (!data || !data.result || !Array.isArray(data.result.data)) {
			Log.error("MMM-News: Unexpected API response format", data);
			return;
		}

		this.newsByCategory[categoryKey] = data.result.data.slice(0, this.config.maxNewsItems);
		this.updateDom(400);
	},

	fetchAllCategories: function () {
		this.config.categories.forEach((category) => this.fetchCategory(category.key));
	},

	fetchCategory: function (categoryKey) {
		if (this.loadingCategories.has(categoryKey)) {
			return;
		}

		this.loadingCategories.add(categoryKey);
		this.sendSocketNotification("FETCH_NEWS", {
			url: this.config.apiUrl,
			key: this.config.apiKey,
			type: categoryKey
		});
	},

	scheduleNextUpdate: function () {
		const now = new Date();
		let nextUpdate = null;
		let earliestTime = null;

		this.config.updateSchedule.forEach((schedule) => {
			const scheduleTime = new Date();
			scheduleTime.setHours(schedule.hour, schedule.minute, 0, 0);
			if (scheduleTime > now && (!nextUpdate || scheduleTime < nextUpdate)) {
				nextUpdate = scheduleTime;
			}
			if (!earliestTime || scheduleTime < earliestTime) {
				earliestTime = scheduleTime;
			}
		});

		if (!nextUpdate) {
			nextUpdate = new Date(earliestTime);
			nextUpdate.setDate(nextUpdate.getDate() + 1);
		}

		clearTimeout(this.refreshTimer);
		this.refreshTimer = setTimeout(() => {
			this.fetchAllCategories();
			this.scheduleNextUpdate();
		}, nextUpdate.getTime() - now.getTime());
	},

	getActiveCategory: function () {
		return this.config.categories[this.activeCategoryIndex] || this.config.categories[0];
	},

	getActiveNews: function () {
		const activeCategory = this.getActiveCategory();
		return this.newsByCategory[activeCategory.key] || [];
	},

	resolvePanelTitle: function () {
		if (this.config.panelTitleKey) {
			return this.translate(this.config.panelTitleKey, this.config.panelTitle || this.name);
		}

		return this.config.panelTitle || this.name;
	},

	resolveCategoryLabel: function (category) {
		if (category.labelKey) {
			return this.translate(category.labelKey, category.label || category.key);
		}

		return category.label || category.key;
	},

	switchCategory: function (direction) {
		const total = this.config.categories.length;
		this.activeCategoryIndex = (this.activeCategoryIndex + direction + total) % total;
		const activeCategory = this.getActiveCategory();
		if (!this.newsByCategory[activeCategory.key]) {
			this.fetchCategory(activeCategory.key);
		}
		this.updateDom(260);
	},

	handleCategoryClick: function (index) {
		this.activeCategoryIndex = index;
		const activeCategory = this.getActiveCategory();
		if (!this.newsByCategory[activeCategory.key]) {
			this.fetchCategory(activeCategory.key);
		}
		this.updateDom(220);
	},

	buildHeader: function () {
		const header = document.createElement("div");
		header.className = "news-header";

		const title = document.createElement("div");
		title.className = "news-panel-title";
		title.textContent = this.resolvePanelTitle();
		header.appendChild(title);

		const hint = document.createElement("div");
		hint.className = "news-panel-hint";
		hint.textContent = this.translate("SWIPE_HINT", "← Swipe to switch categories →");
		header.appendChild(hint);

		return header;
	},

	buildTabs: function () {
		const tabs = document.createElement("div");
		tabs.className = "news-tabs";

		this.config.categories.forEach((category, index) => {
			const tab = document.createElement("button");
			tab.className = `news-tab${index === this.activeCategoryIndex ? " is-active" : ""}`;
			tab.textContent = this.resolveCategoryLabel(category);
			tab.addEventListener("click", () => this.handleCategoryClick(index));
			tabs.appendChild(tab);
		});

		return tabs;
	},

	buildNewsList: function () {
		const list = document.createElement("div");
		list.className = "news-list";
		list.style.maxHeight = `${this.config.panelHeight}px`;
		list.addEventListener("pointerdown", (event) => {
			this.pointerStart = { x: event.clientX, y: event.clientY };
		});
		list.addEventListener("pointerup", (event) => {
			if (!this.pointerStart) {
				return;
			}
			const deltaX = event.clientX - this.pointerStart.x;
			const deltaY = event.clientY - this.pointerStart.y;
			this.pointerStart = null;
			if (Math.abs(deltaX) < this.config.swipeThreshold || Math.abs(deltaX) <= Math.abs(deltaY)) {
				return;
			}
			this.switchCategory(deltaX < 0 ? 1 : -1);
		});

		const newsItems = this.getActiveNews();
		if (!newsItems.length) {
			const emptyState = document.createElement("div");
			emptyState.className = "news-empty-state";
			emptyState.textContent = this.loadingCategories.has(this.getActiveCategory().key)
				? this.translate("LOADING_NEWS", "Loading news...")
				: this.translate("EMPTY_NEWS", "No news available");
			list.appendChild(emptyState);
			return list;
		}

		newsItems.forEach((item, index) => {
			const article = document.createElement("article");
			article.className = "news-card-item";

			const order = document.createElement("div");
			order.className = "news-order";
			order.textContent = String(index + 1).padStart(2, "0");
			article.appendChild(order);

			const content = document.createElement("div");
			content.className = "news-content";

			const headline = document.createElement("div");
			headline.className = "news-title";
			headline.textContent = item.title;
			content.appendChild(headline);

			const meta = document.createElement("div");
			meta.className = "news-source";
			const newsDate = item.date ? new Date(item.date) : new Date();
			const author = item.author_name || this.translate("UNKNOWN_SOURCE", "Unknown source");
			meta.textContent = `${author} · ${newsDate.toLocaleString(config.locale || "zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" })}`;
			content.appendChild(meta);

			article.appendChild(content);
			list.appendChild(article);
		});

		return list;
	},

	getDom: function () {
		const wrapper = document.createElement("div");
		wrapper.className = "news-scroller";
		wrapper.appendChild(this.buildHeader());
		wrapper.appendChild(this.buildTabs());
		wrapper.appendChild(this.buildNewsList());
		return wrapper;
	},

	stop: function () {
		clearTimeout(this.refreshTimer);
	}
});

