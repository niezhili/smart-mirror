Module.register("MMM-Quote", {
	defaults: {
		updateInterval: 16000,
		fadeSpeed: 1000,
		authorAlign: "align-right",
		defaultCategory: "鍚嶄汉缁忓吀璇綍",
		categories: ["鍚嶄汉缁忓吀璇綍", "璋氳", "鏂囧"]
	},

	getStyles: function() {
		return ["MMM-Quote.css"];
	},

	getScripts: function() {
		return ["quotes-library.js"];
	},

	start: function() {
		this.library = [];
		this.currentCategoryIndex = Math.max(0, this.config.categories.indexOf(this.config.defaultCategory));
		this.currentQuote = null;
		this.refreshLibrary();
		this.pickQuote();
		this.interval = setInterval(() => this.pickQuote(), this.config.updateInterval);
	},

	refreshLibrary: function() {
		this.library = Array.isArray(window.MMMQuotesLibrary) ? window.MMMQuotesLibrary : [];
	},

	getCurrentCategory: function() {
		return this.config.categories[this.currentCategoryIndex] || this.config.categories[0];
	},

	getCategoryQuotes: function() {
		const category = this.getCurrentCategory();
		return this.library.filter((item) => item.category === category);
	},

	pickQuote: function() {
		this.refreshLibrary();
		const quotes = this.getCategoryQuotes();
		if (!quotes.length) {
			this.currentQuote = null;
			this.updateDom(this.config.fadeSpeed);
			return;
		}

		let nextQuote = quotes[Math.floor(Math.random() * quotes.length)];
		if (this.currentQuote && quotes.length > 1) {
			while (nextQuote.quote === this.currentQuote.quote) {
				nextQuote = quotes[Math.floor(Math.random() * quotes.length)];
			}
		}

		this.currentQuote = nextQuote;
		this.updateDom(this.config.fadeSpeed);
	},

	switchCategory: function(index) {
		this.currentCategoryIndex = index;
		this.pickQuote();
	},

	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "quote-card";
		wrapper.addEventListener("click", () => this.pickQuote());

		const header = document.createElement("div");
		header.className = "quote-header";
		this.config.categories.forEach((category, index) => {
			const pill = document.createElement("button");
			pill.className = `quote-category${index === this.currentCategoryIndex ? " is-active" : ""}`;
			pill.type = "button";
			pill.textContent = category;
			pill.addEventListener("click", (event) => {
				event.stopPropagation();
				this.switchCategory(index);
			});
			header.appendChild(pill);
		});
		wrapper.appendChild(header);

		const body = document.createElement("div");
		body.className = "quote-body";

		if (!this.currentQuote) {
			const emptyState = document.createElement("div");
			emptyState.className = "quote-empty";
			emptyState.textContent = "褰撳墠鍒嗙被鏆傛棤璇綍锛岀偣鍑诲垎绫绘垨绋嶅悗閲嶈瘯銆?;
			body.appendChild(emptyState);
			wrapper.appendChild(body);
			return wrapper;
		}

		const quoteText = document.createElement("div");
		quoteText.className = "quote-text";
		quoteText.textContent = `鈥?{this.currentQuote.quote}鈥漙;
		body.appendChild(quoteText);

		const footer = document.createElement("div");
		footer.className = `quote-footer ${this.config.authorAlign}`;
		footer.textContent = `${this.currentQuote.author} 路 ${this.currentQuote.source}`;
		body.appendChild(footer);

		wrapper.appendChild(body);
		return wrapper;
	},

	stop: function() {
		clearInterval(this.interval);
	}
});

