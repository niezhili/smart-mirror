const NodeHelper = require("node_helper");

module.exports = NodeHelper.create({
	// 模块启动时执行
	start: function () {
		console.log("CustomClock模块已启动");
	},

	// 处理前端发送的通知
	socketNotificationReceived: function (notificationType, payload) {
		if (notificationType === "CONFIG") {
			this.moduleConfig = payload;
		}
	},

	
});