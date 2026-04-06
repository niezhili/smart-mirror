Module.register("MMM-Quote", {
	defaults: {
		updateInterval: 16000,
		fadeSpeed: 1000,
		authorAlign: "align-right",
		defaultCategory: "famous",
		categories: [
			{ key: "famous", dataCategory: "名人经典语录", labelKey: "CATEGORY_FAMOUS" },
			{ key: "proverb", dataCategory: "谚语", labelKey: "CATEGORY_PROVERB" },
			{ key: "literature", dataCategory: "文学", labelKey: "CATEGORY_LITERATURE" }
		]
	},

	fallbackQuotes: [
		{ category: "名人经典语录", quote: "生活就像骑自行车。要保持平衡，就得向前走。", author: "爱因斯坦", source: "人生哲学" },
		{ category: "名人经典语录", quote: "每个人都应该有梦想，梦想是人生的灯塔。", author: "莎士比亚", source: "戏剧作品" },
		{ category: "谚语", quote: "千里之行，始于足下。", author: "老子", source: "道德经" },
		{ category: "谚语", quote: "一寸光阴一寸金，寸金难买寸光阴。", author: "民间谚语", source: "古代智慧" },
		{ category: "文学", quote: "世界以痛吻我，要求我报之以歌。", author: "泰戈尔", source: "飞鸟集" },
		{ category: "文学", quote: "未经审视的人生不值得活。", author: "苏格拉底", source: "哲学思想" }
	],

	getStyles: function() {
		return ["MMM-Quote.css"];
	},

	getScripts: function() {
		return ["quotes-library.js"];
	},

	getTranslations: function() {
		return {
			en: "translations/en.json",
			"zh-cn": "translations/zh-cn.json"
		};
	},

	start: function() {
		this.library = [];
		const categories = this.getConfiguredCategories();
		this.currentCategoryIndex = Math.max(0, categories.findIndex((category) => category.key === this.config.defaultCategory || category.dataCategory === this.config.defaultCategory));
		this.currentQuote = null;
		this.dom = null;
		this.refreshLibrary();
		this.pickQuote();
		this.interval = setInterval(() => this.pickQuote(), this.config.updateInterval);
	},

	getConfiguredCategories: function() {
		return this.config.categories.map((category) => {
			if (typeof category === "string") {
				return {
					key: category,
					dataCategory: category,
					label: category
				};
			}

			return {
				key: category.key || category.dataCategory,
				dataCategory: category.dataCategory || category.key,
				label: category.label,
				labelKey: category.labelKey
			};
		});
	},

	resolveCategoryLabel: function(category) {
		if (category.labelKey) {
			return this.translate(category.labelKey, category.label || category.dataCategory);
		}

		return category.label || category.dataCategory;
	},

	refreshLibrary: function() {
		this.library = Array.isArray(window.MMMQuotesLibrary) && window.MMMQuotesLibrary.length
			? window.MMMQuotesLibrary
			: this.fallbackQuotes;
	},

	getCurrentCategory: function() {
		const categories = this.getConfiguredCategories();
		return categories[this.currentCategoryIndex] || categories[0];
	},

	getCategoryQuotes: function() {
		const category = this.getCurrentCategory();
		return this.library.filter((item) => item.category === category.dataCategory);
	},

	pickQuote: function() {
		this.refreshLibrary();
		const quotes = this.getCategoryQuotes();
		if (!quotes.length) {
			this.currentQuote = null;
			this.renderQuote();
			return;
		}

		let nextQuote = quotes[Math.floor(Math.random() * quotes.length)];
		if (this.currentQuote && quotes.length > 1) {
			while (nextQuote.quote === this.currentQuote.quote) {
				nextQuote = quotes[Math.floor(Math.random() * quotes.length)];
			}
		}

		this.currentQuote = nextQuote;
		this.renderQuote();
	},

	switchCategory: function(index) {
		this.currentCategoryIndex = index;
		this.pickQuote();
	},

	getDom: function() {
		if (this.dom && this.dom.wrapper) {
			return this.dom.wrapper;
		}

		const wrapper = document.createElement("div");
		wrapper.className = "quote-card";
		wrapper.addEventListener("click", () => this.pickQuote());

		const header = document.createElement("div");
		header.className = "quote-header";
		const categoryButtons = [];
		this.getConfiguredCategories().forEach((category, index) => {
			const pill = document.createElement("button");
			pill.className = `quote-category${index === this.currentCategoryIndex ? " is-active" : ""}`;
			pill.type = "button";
			pill.textContent = this.resolveCategoryLabel(category);
			pill.addEventListener("click", (event) => {
				event.stopPropagation();
				this.switchCategory(index);
			});
			header.appendChild(pill);
			categoryButtons.push(pill);
		});
		wrapper.appendChild(header);

		const body = document.createElement("div");
		body.className = "quote-body";

		const emptyState = document.createElement("div");
		emptyState.className = "quote-empty";
		emptyState.textContent = this.translate("EMPTY_QUOTES", "No quotes available in this category.");

		const quoteText = document.createElement("div");
		quoteText.className = "quote-text";

		const footer = document.createElement("div");
		footer.className = `quote-footer ${this.config.authorAlign}`;

		body.appendChild(emptyState);
		body.appendChild(quoteText);
		body.appendChild(footer);

		wrapper.appendChild(body);
		this.dom = {
			wrapper,
			categoryButtons,
			emptyState,
			quoteText,
			footer
		};
		this.renderQuote();
		return wrapper;
	},

	renderQuote: function() {
		if (!this.dom) {
			this.updateDom(0);
			return;
		}

		this.dom.categoryButtons.forEach((button, index) => {
			button.classList.toggle("is-active", index === this.currentCategoryIndex);
		});

		if (!this.currentQuote) {
			this.dom.emptyState.style.display = "block";
			this.dom.quoteText.style.display = "none";
			this.dom.footer.style.display = "none";
			return;
		}

		// 此处已重构，改为原位更新文本，避免定时器触发整块重绘导致闪烁。
		this.dom.emptyState.style.display = "none";
		this.dom.quoteText.style.display = "block";
		this.dom.footer.style.display = "block";
		this.dom.quoteText.textContent = `“${this.currentQuote.quote}”`;
		this.dom.footer.textContent = `${this.currentQuote.author} · ${this.currentQuote.source}`;
	},

	stop: function() {
		clearInterval(this.interval);
	}
});

