const NodeHelper = require("node_helper");
const axios = require("axios");

module.exports = NodeHelper.create({
    start: function() {
        console.log("Starting node helper for MMM-CustomWeather...");
    },

    async getCoordinates() {
        try {
            // Check if we have cached coordinates and if enough time has passed
            const now = Date.now();
            if (this.cachedCoordinates && (now - this.lastFetch) < this.retryDelay) {
                return this.cachedCoordinates;
            }

            // Add delay if we're retrying too soon
            if (now - this.lastFetch < this.retryDelay) {
                console.log(`[${this.name}] Rate limit - waiting before retry`);
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
            }

			const ipApiUrl = `https://ipapi.co/json/`;
            const response = await axios.get(ipApiUrl, {
                timeout: 5000,
                headers: {
                    'User-Agent': 'MagicMirror/1.0'
                }
            });

            this.lastFetch = Date.now();
			this.cachedCoordinates = {
				lat: response.data.latitude,
                long: response.data.longitude,
				city: response.data.city
            };
            return this.cachedCoordinates;

        } catch (error) {
            console.error(`[${this.name}] Error fetching coordinates:`, error);
            // Return cached coordinates if available
            if (this.cachedCoordinates) {
                return this.cachedCoordinates;
            }

			// Return fallback coordinates if no cache
            return { lat: 0, long: 0 }; // You should set appropriate fallback coordinates
        }
    },
    socketNotificationReceived: async function(notification, payload) {

		if (notification === "GET_LOCATION") {
            try {
                // const coords = await this.getCoordinates();
                this.sendSocketNotification("LOCATION_RESULT", {});
                // this.sendSocketNotification("LOCATION_RESULT", coords);
            } catch (error) {
                console.error(`[${this.name}] Location error:`, error.message);
                this.sendSocketNotification("LOCATION_ERROR", error.message);
            }
        } else if (notification === "FETCH_DATA") {
            try {
                const response = await axios.get(payload.url);
                this.sendSocketNotification("DATA_FETCHED", response.data);
            } catch (error) {
                console.error(`[${this.name}] Weather data error:`, error.message);
                console.error(`[${this.name}] Attempted URL: ${payload.url}`);
                this.sendSocketNotification("FETCH_ERROR", error.message);
            }
        }
    }
});
