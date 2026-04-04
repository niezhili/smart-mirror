// node_helper.js
const NodeHelper = require("node_helper");
const languageState = require("./language-state.js");

module.exports = NodeHelper.create({
	socketNotificationReceived: function(notification, payload) {
		if (notification === "GET_LANGUAGE") {
			const language = languageState.getLanguage();
			this.sendSocketNotification("CURRENT_LANGUAGE", language);
		}

		if (notification === "SET_LANGUAGE") {
			languageState.setLanguage(payload);
			this.sendSocketNotification("CURRENT_LANGUAGE", payload);
		}
	}
});
