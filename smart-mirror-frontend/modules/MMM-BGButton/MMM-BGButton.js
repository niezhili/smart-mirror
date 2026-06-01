Module.register("MMM-BGButton", {
	defaults: {},

	start: function () {
		Log.info("Starting module: " + this.name);
	},

	getStyles: function () {
		return ["MMM-BGButton.css"];
	},

	getDom: function () {
		var wrapper = document.createElement("div");
		wrapper.className = "bg-button-wrapper";

		var btn = document.createElement("button");
		btn.className = "bg-change-btn";
		btn.innerHTML = "🖼️";

		var self = this;
		btn.addEventListener("click", function () {
			self.sendNotification("CHANGE_BACKGROUND");

			// Pulse animation feedback
			btn.classList.add("pulse");
			setTimeout(function () {
				btn.classList.remove("pulse");
			}, 400);
		});

		wrapper.appendChild(btn);
		return wrapper;
	}
});
