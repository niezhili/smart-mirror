const NodeHelper = require("node_helper");
const https = require("https");

module.exports = NodeHelper.create({
start: function() {
this.config = null;
},

socketNotificationReceived: function(notification, payload) {
if (notification === "INIT") {
this.config = payload;
return;
}

if (notification === "FETCH_NEWS") {
this.fetchNews(payload);
}
},

fetchNews: function(params) {
const url = `${params.url}?key=${params.key}&type=${params.type}`;
https.get(url, (response) => {
let data = "";
response.on("data", (chunk) => {
data += chunk;
});
response.on("end", () => {
try {
this.sendSocketNotification("NEWS_RESULT", {
type: params.type,
data: JSON.parse(data)
});
} catch (error) {
this.sendSocketNotification("NEWS_RESULT", {
type: params.type,
error: error.message
});
}
});
}).on("error", (error) => {
this.sendSocketNotification("NEWS_RESULT", {
type: params.type,
error: error.message
});
});
}
});
