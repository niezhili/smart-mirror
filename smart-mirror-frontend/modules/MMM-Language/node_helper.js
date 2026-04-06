const NodeHelper = require("node_helper");
const languageState = require("./language-state.js");

module.exports = NodeHelper.create({
socketNotificationReceived: function(notification, payload) {
if (notification === "GET_LANGUAGE") {
this.sendSocketNotification("CURRENT_LANGUAGE", languageState.getLanguage());
}

if (notification === "SET_LANGUAGE") {
languageState.setLanguage(payload);
this.sendSocketNotification("CURRENT_LANGUAGE", languageState.getLanguage());
}
}
});
