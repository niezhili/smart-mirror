/* MagicMirror² Custom Clock Module */

Module.register("MMM-CustomClock", {
	// 模块默认配置
	defaults: {
		displayType: "digital", // 显示类型：digital(数字), analog(模拟), both(两者)
		language: config.language, // 语言设置，默认继承全局
		timezone: null, // 时区设置
		// 数字时钟设置
		timeFormat: 24, // 时间格式：12或24小时制
		displaySeconds: true, // 是否显示秒
		showPeriod: true, // 是否显示上/下午
		showPeriodUpper: false, // 上/下午是否大写
		// 模拟时钟设置
		clockBold: false, // 时钟是否加粗
		showDate: true, // 是否显示日期
		analogFace: "simple", // 模拟时钟表盘
		analogSize: "200px", // 模拟时钟大小
		analogPlacement: "bottom", // 模拟时钟位置
		secondsColor: "#888888", // 秒针颜色
		// 日期设置
		dateFormat: "default", // 日期格式，默认按语言自适应
		showWeek: false, // 是否显示周数
	},

	// 引入样式文件
	getStyles: function () {
		return ["customclock.css"];
	},

	// 启动模块
	start: function () {
		Log.info(`Starting module: ${this.name}`);
		this.sendSocketNotification("CONFIG", this.config);

		// Color cycling state
		this._colorIndex = 0;
		this._colorPalette = [
			null,        // default (inherit)
			"#ffffff",   // white
			"#00e5ff",   // cyan
			"#76ff03",   // green
			"#ffab00",   // orange
			"#ff4081"    // pink
		];
		
		// 计算下次更新延迟时间
		const calculateNextUpdateDelay = () => {
			const currentTime = new Date();
			// 不显示秒时，每分钟更新一次
			return this.config.displaySeconds 
				? 1000 
				: (60 - currentTime.getSeconds()) * 1000;
		};

		// 递归调度更新（避免时间漂移）
		const scheduleNextUpdate = () => {
			this.updateDom();
			setTimeout(scheduleNextUpdate, calculateNextUpdateDelay());
		};

		// 启动更新计时器
		setTimeout(scheduleNextUpdate, calculateNextUpdateDelay());
	},

	// 处理来自后端的通知
	socketNotificationReceived: function (notification) {
		if (notification === "HIDE_MODULE") {
			this.hide(1000);
		} else if (notification === "SHOW_MODULE") {
			this.show(1000);
		}
	},

	/**
	 * 根据背景色计算高对比度文本色
	 * @param {string} bgColor - 背景色（rgb或hex格式）
	 * @returns {string} 高对比度文本色
	 */
	getHighContrastColor: function (bgColor) {
		// 解析RGB值
		let red, green, blue;
		if (bgColor.startsWith('#')) {
			// 处理十六进制颜色（如#fff或#ffffff）
			const hex = bgColor.slice(1).padEnd(6, 'f');
			red = parseInt(hex.substring(0, 2), 16);
			green = parseInt(hex.substring(2, 4), 16);
			blue = parseInt(hex.substring(4, 6), 16);
		} else if (bgColor.startsWith('rgb')) {
			// 处理rgb(r, g, b)格式
			const rgbValues = bgColor.match(/\d+/g).map(Number);
			[red, green, blue] = rgbValues;
		} else {
			// 默认白色背景用黑色文本
			return '#000000';
		}

		// 计算相对亮度（WCAG标准公式）
		const luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255;
		// 亮度>0.5用黑色，否则用白色
		return luminance > 0.1 ? '#000000' : '#ffffff';
	},

	/**
	 * 根据语言格式化日期
	 * @param {Date} date - 日期对象
	 * @returns {string} 格式化后的日期字符串
	 */
	formatDateByLanguage: function (date) {
		const lang = config.language || 'en-US';
		// 不同语言的日期格式配置
		const dateOptions = {
			'zh-CN': { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }, // 星期一，2024年5月20日
			'en-US': { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }, // Monday, May 20, 2024
			'ja-JP': { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }, // 月曜日、2024年5月20日
			'de-DE': { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }  // Montag, 20. Mai 2024
		};

		// 使用对应语言的格式配置，默认使用英文格式
		const options = dateOptions[lang] || dateOptions['en-US'];
		return date.toLocaleDateString(lang, options);
	},

	/**
	 * 格式化时间
	 * @param {Date} date - 日期对象
	 * @returns {string} 格式化后的时间字符串
	 */
	formatTime: function (date) {
		let hours = date.getHours();
		const minutes = date.getMinutes().toString().padStart(2, "0");
		const seconds = date.getSeconds().toString().padStart(2, "0");
		let period = "";

		// 处理12小时制
		if (this.config.timeFormat !== 24) {
			period = hours >= 12 ? " PM" : " AM";
			hours = hours % 12;
			hours = hours || 12; // 0点转为12点
		}

		// 基础时间字符串
		let timeString = `${hours}:${minutes}:${seconds}`;

		// 添加上/下午标识
		if (this.config.timeFormat !== 24 && this.config.showPeriod) {
			timeString += this.config.showPeriodUpper ? period : period.toLowerCase();
		}

		return timeString;
	},

	// 创建模块DOM元素
	getDom: function () {
		const container = document.createElement("div");
		container.className = "customclock-grid";

		// 获取当前时间（支持时区）
		const currentTime = new Date();
		let displayDate = new Date(currentTime);

		// 应用时区设置
		if (this.config.timezone) {
			try {
				const timeZoneOptions = { timeZone: this.config.timezone };
				const formatter = new Intl.DateTimeFormat('en-US', timeZoneOptions);
				displayDate = new Date(formatter.format(currentTime));
			} catch (error) {
				console.error("时区设置错误:", error);
			}
		}

		// 创建数字时钟
		if (this.config.displayType !== "analog") {
			const digitalContainer = document.createElement("div");
			digitalContainer.className = "digital";

			// 显示日期
			if (this.config.showDate) {
				const dateElement = document.createElement("div");
				dateElement.className = "date normal medium";
				dateElement.textContent = this.formatDateByLanguage(displayDate);
				digitalContainer.appendChild(dateElement);
			}

			// 显示时间
			const timeElement = document.createElement("div");
			timeElement.className = "time bright large light";
			timeElement.textContent = this.formatTime(displayDate);

			// 应用加粗样式
			if (this.config.clockBold) {
				timeElement.innerHTML = timeElement.textContent.replace(
					/(\d{1,2}):(\d{2})/,
					"$1<span class='bold'>:$2</span>"
				);
			}

			digitalContainer.appendChild(timeElement);

			// 显示周数
			if (this.config.showWeek) {
				const weekElement = document.createElement("div");
				weekElement.className = "week dimmed medium";
				
				// 计算周数
				const firstDayOfYear = new Date(displayDate.getFullYear(), 0, 1);
				const pastDays = (displayDate - firstDayOfYear) / 86400000;
				const weekNumber = Math.ceil((pastDays + firstDayOfYear.getDay() + 1) / 7);
				
				weekElement.textContent = `Week ${weekNumber}`;
				digitalContainer.appendChild(weekElement);
			}

			container.appendChild(digitalContainer);
		}

		// 创建模拟时钟
		if (this.config.displayType !== "digital") {
			const analogContainer = document.createElement("div");
			analogContainer.className = "clock-circle";
			analogContainer.style.width = this.config.analogSize;
			analogContainer.style.height = this.config.analogSize;

			// 设置表盘样式
			if (this.config.analogFace && this.config.analogFace !== "simple" && this.config.analogFace !== "none") {
				analogContainer.style.background = `url(${this.data.path}faces/${this.config.analogFace}.svg)`;
				analogContainer.style.backgroundSize = "100%";
				analogContainer.style.border = "rgba(0, 0, 0, 0.1)";
			} else if (this.config.analogFace !== "none") {
				analogContainer.style.border = "2px solid"; // 边框颜色后续动态设置
			}

			// 时钟面板
			const clockFace = document.createElement("div");
			clockFace.className = "clock-face";

			// 时针
			const hours = displayDate.getHours() % 12;
			const minutes = displayDate.getMinutes();
			const hourDegrees = (hours * 30) + (minutes * 0.5) + 90; // 每小时30度，分钟影响偏移
			const hourHand = document.createElement("div");
			hourHand.className = "clock-hour";
			hourHand.style.transform = `rotate(${hourDegrees}deg)`;

			// 分针
			const minuteDegrees = (minutes * 6) + 90; // 每分钟6度
			const minuteHand = document.createElement("div");
			minuteHand.className = "clock-minute";
			minuteHand.style.transform = `rotate(${minuteDegrees}deg)`;

			clockFace.appendChild(hourHand);
			clockFace.appendChild(minuteHand);

			// 秒针
			if (this.config.displaySeconds) {
				const seconds = displayDate.getSeconds();
				const secondDegrees = (seconds * 6) + 90;
				const secondHand = document.createElement("div");
				secondHand.className = "clock-second";
				secondHand.style.transform = `rotate(${secondDegrees}deg)`;
				clockFace.appendChild(secondHand);
			}

			analogContainer.appendChild(clockFace);
			container.appendChild(analogContainer);
		}

		// 设置布局
		if (this.config.displayType === "both") {
			container.classList.add(`clock-grid-${this.config.analogPlacement}`);
		}

		// 动态设置对比度颜色
		setTimeout(() => {
			const computedStyle = window.getComputedStyle(container);
			const bgColor = computedStyle.backgroundColor;
			const textColor = this.getHighContrastColor(bgColor);

			// 设置数字时钟文本颜色
			container.querySelectorAll('.digital .time, .digital .date, .digital .week')
				.forEach(el => el.style.color = textColor);

			// 设置模拟时钟元素颜色
			container.querySelectorAll('.clock-hour, .clock-minute, .clock-circle')
				.forEach(el => el.style.backgroundColor = textColor);
				
			// 秒针颜色保持配置但增强对比度
			container.querySelectorAll('.clock-second')
				.forEach(el => el.style.backgroundColor = this.getHighContrastColor(bgColor));
		}, 0);

		// Click to cycle text color
		container.style.cursor = "pointer";
		var self = this;
		container.addEventListener("click", function (event) {
			event.stopPropagation();
			self.cycleColor();
		});

		return container;
	},

	/**
	 * Cycle through a palette of text colors on click.
	 */
	cycleColor: function () {
		this._colorIndex = (this._colorIndex + 1) % this._colorPalette.length;
		var color = this._colorPalette[this._colorIndex];

		var container = document.querySelector("#" + this.identifier + " .module-content");
		if (container) {
			if (color) {
				container.style.color = color;
				container.style.transition = "color 0.5s ease";
			} else {
				container.style.color = "";
			}
		}

		var colorName = color || "default";
		Log.info(this.name + ": color changed to " + colorName);
	},

	notificationReceived: function (notification, payload, sender) {
		if (notification === "LANGUAGE_CHANGED") {
			this.updateDom(0);
		}
	}
});