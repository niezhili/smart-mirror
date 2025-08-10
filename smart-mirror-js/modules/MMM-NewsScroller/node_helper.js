const NodeHelper = require('node_helper');
const https = require('https');

module.exports = NodeHelper.create({
	start: function() {
		console.log("Starting node helper for: MMM-NewsScroller");
		this.config = null;
	},

	socketNotificationReceived: function(notification, payload) {
		if (notification === "INIT") {
			this.config = payload;
			console.log("MMM-NewsScroller helper initialized");
		}
		if (notification === "FETCH_NEWS") {

			this.fetchNews(payload);
		}
	},

	fetchNews: function(params) {
		const url = `${params.url}?key=${params.key}&type=${params.type}`;

		https.get(url, (res) => {
			let data = '';

			res.on('data', (chunk) => {
				data += chunk;
			});

			res.on('end', () => {
				try {
					const jsonData = JSON.parse(data);
					this.sendSocketNotification("NEWS_RESULT", { data: jsonData });
				} catch (e) {
					console.error("MMM-NewsScroller helper: Error parsing JSON", e);
					this.sendSocketNotification("NEWS_RESULT", { error: "Invalid JSON response" });
				}
			});
		}).on('error', (e) => {
			console.error("MMM-NewsScroller helper: Error fetching news", e.message);
			this.sendSocketNotification("NEWS_RESULT", { error: e.message });
		});
	}
});
