/* MMM-Quote — Quote module with swipe navigation */

Module.register("MMM-Quote", {
	defaults: {
		updateInterval: 60 * 60 * 1000, // refresh quotes every hour
		fallbackQuotes: [
			{ content: "The only way to do great work is to love what you do.", author: "Steve Jobs" },
			{ content: "生活就像一盒巧克力，你永远不知道下一颗是什么味道。", author: "《阿甘正传》" },
			{ content: "活着本身就是意义。", author: "余华" },
			{ content: "Stay hungry, stay foolish.", author: "Steve Jobs" },
			{ content: "千里之行，始于足下。", author: "老子" },
			{ content: "The best time to plant a tree was 20 years ago. The second best time is now.", author: "Chinese Proverb" }
		]
	},

	start: function () {
		Log.info("Starting module: " + this.name);
		this.currentQuoteIndex = 0;
		this.quotes = this.config.fallbackQuotes;
		this.loaded = true;

		// Register with shared interaction controller
		if (window.InteractionController) {
			InteractionController.register(this, {
				getExpandedContent: this.getExpandedContent.bind(this)
			});
		}
	},

	getStyles: function () {
		return ["MMM-Quote.css"];
	},

	getDom: function () {
		var wrapper = document.createElement("div");
		wrapper.className = "quote-container";

		if (!this.loaded || this.quotes.length === 0) {
			wrapper.innerHTML = "Loading...";
			wrapper.className = "quote-container dimmed light small";
			return wrapper;
		}

		var quote = this.quotes[this.currentQuoteIndex];

		var contentDiv = document.createElement("div");
		contentDiv.className = "quote-content";
		contentDiv.textContent = '"' + quote.content + '"';

		var authorDiv = document.createElement("div");
		authorDiv.className = "quote-author";
		authorDiv.textContent = "— " + quote.author;

		wrapper.appendChild(contentDiv);
		wrapper.appendChild(authorDiv);

		// Swipe left/right to navigate quotes
		if (window.InteractionController) {
			var self = this;
			InteractionController.addSwipeListeners(wrapper, {
				onSwipeLeft: function () {
					self.nextQuote();
				},
				onSwipeRight: function () {
					self.previousQuote();
				},
				threshold: 50
			});
		}

		// Click to expand
		wrapper.style.cursor = "pointer";
		wrapper.addEventListener("click", function (event) {
			event.stopPropagation();
			if (window.InteractionController) {
				InteractionController.expand(this);
			}
		}.bind(this));

		return wrapper;
	},

	nextQuote: function () {
		if (this.quotes.length === 0) return;
		this.currentQuoteIndex = (this.currentQuoteIndex + 1) % this.quotes.length;
		this.updateDom(300);
	},

	previousQuote: function () {
		if (this.quotes.length === 0) return;
		this.currentQuoteIndex = (this.currentQuoteIndex - 1 + this.quotes.length) % this.quotes.length;
		this.updateDom(300);
	},

	getExpandedContent: function () {
		var container = document.createElement("div");
		container.className = "quote-expanded-container";

		var quote = this.quotes[this.currentQuoteIndex];

		var contentDiv = document.createElement("div");
		contentDiv.className = "quote-expanded-content";
		contentDiv.textContent = '"' + quote.content + '"';

		var authorDiv = document.createElement("div");
		authorDiv.className = "quote-expanded-author";
		authorDiv.textContent = "— " + quote.author;

		container.appendChild(contentDiv);
		container.appendChild(authorDiv);

		return container;
	},

	notificationReceived: function (notification, payload, sender) {
		if (notification === "LANGUAGE_CHANGED") {
			this.updateDom(0);
		}
	}
});
