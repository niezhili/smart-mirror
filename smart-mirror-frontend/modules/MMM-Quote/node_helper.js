const NodeHelper = require("node_helper");

module.exports = NodeHelper.create({
	start: function () {
		console.log("MMM-Quote node_helper started");
	}

	// Future: fetch quotes from an external API here
});
