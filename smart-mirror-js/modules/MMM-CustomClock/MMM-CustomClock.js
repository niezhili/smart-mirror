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
		clockBold: true, // 时钟是否加粗
		showDate: true, // 是否显示日期
		analogFace: "simple", // 模拟时钟表盘
		analogSize: "200px", // 模拟时钟大小
		analogPlacement: "bottom", // 模拟时钟位置
		secondsColor: "#888888", // 秒针颜色
		// 日期设置
		dateFormat: "default", // 日期格式，默认按语言自适应
		showWeek: false, // 是否显示周数
		// 新增配置：自动检测背景
		autoDetectBackground: true, // 是否自动检测背景色
		fallbackTextColor: null, // 手动指定文本颜色（覆盖自动检测）
	},

	// 引入样式文件
	getStyles: function () {
		return ["customclock.css"];
	},

	// 启动模块
	start: function () {
		Log.info(`Starting module: ${this.name}`);
		this.sendSocketNotification("CONFIG", this.config);

		// 初始化颜色缓存
		this.cachedBackgroundColor = null;
		this.cachedTextColor = null;
		this.colorDetectionComplete = false;

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
	 * 检测实际的背景颜色（向上遍历DOM树） - 缓存版本
	 * @param {HTMLElement} element - 起始元素
	 * @returns {string} 实际背景色
	 */
	getActualBackgroundColor: function (element) {
		// 如果已经检测过且结果有效，直接返回缓存
		if (this.cachedBackgroundColor && this.colorDetectionComplete) {
			return this.cachedBackgroundColor;
		}

		let currentElement = element;
		let bgColor = 'rgba(0, 0, 0, 0)';

		// 向上遍历DOM树，寻找第一个有实际背景色的元素
		while (currentElement && currentElement !== document.documentElement) {
			const computedStyle = window.getComputedStyle(currentElement);
			const currentBgColor = computedStyle.backgroundColor;

			// 检查是否为非透明背景
			if (currentBgColor &&
				currentBgColor !== 'rgba(0, 0, 0, 0)' &&
				currentBgColor !== 'transparent' &&
				currentBgColor !== 'inherit') {
				bgColor = currentBgColor;
				console.log(`在元素 ${currentElement.className || currentElement.tagName} 找到背景色: ${bgColor}`);
				break;
			}
			currentElement = currentElement.parentElement;
		}

		// 如果仍然是透明，检查body和html
		if (bgColor === 'rgba(0, 0, 0, 0)') {
			const bodyBg = window.getComputedStyle(document.body).backgroundColor;
			const htmlBg = window.getComputedStyle(document.documentElement).backgroundColor;

			if (bodyBg && bodyBg !== 'rgba(0, 0, 0, 0)' && bodyBg !== 'transparent') {
				bgColor = bodyBg;
				console.log(`使用body背景色: ${bgColor}`);
			} else if (htmlBg && htmlBg !== 'rgba(0, 0, 0, 0)' && htmlBg !== 'transparent') {
				bgColor = htmlBg;
				console.log(`使用html背景色: ${bgColor}`);
			} else {
				// 最终回退：根据MagicMirror主题判断
				bgColor = this.detectMagicMirrorTheme();
				console.log(`使用主题检测结果: ${bgColor}`);
			}
		}

		// 缓存结果
		this.cachedBackgroundColor = bgColor;
		return bgColor;
	},

	/**
	 * 检测MagicMirror主题
	 * @returns {string} 主题背景色
	 */
	detectMagicMirrorTheme: function () {
		// 检查常见的MagicMirror CSS类
		const body = document.body;
		const html = document.documentElement;

		// 检查是否有深色主题类
		if (body.classList.contains('dark') ||
			html.classList.contains('dark') ||
			body.classList.contains('black') ||
			html.classList.contains('black')) {
			return '#000000'; // 黑色背景
		}

		// 检查CSS变量
		const rootStyle = getComputedStyle(html);
		const bgVar = rootStyle.getPropertyValue('--background-color') ||
			rootStyle.getPropertyValue('--bg-color') ||
			rootStyle.getPropertyValue('--main-bg');

		if (bgVar && bgVar.trim() !== '') {
			return bgVar.trim();
		}

		// 检查页面整体色调（通过采样像素）
		try {
			return this.detectColorByImageData();
		} catch (error) {
			console.warn("无法通过像素采样检测颜色:", error);
		}

		// 默认假设为黑色背景（MagicMirror常见配置）
		return '#000000';
	},

	/**
	 * 通过canvas采样检测主要背景色
	 * @returns {string} 检测到的背景色
	 */
	detectColorByImageData: function () {
		// 创建临时canvas用于采样
		const canvas = document.createElement('canvas');
		const ctx = canvas.getContext('2d');
		canvas.width = 100;
		canvas.height = 100;

		// 在页面角落采样
		try {
			const imageData = ctx.getImageData(10, 10, 80, 80);
			const data = imageData.data;
			let r = 0, g = 0, b = 0, count = 0;

			// 计算平均颜色
			for (let i = 0; i < data.length; i += 4) {
				r += data[i];
				g += data[i + 1];
				b += data[i + 2];
				count++;
			}

			r = Math.round(r / count);
			g = Math.round(g / count);
			b = Math.round(b / count);

			return `rgb(${r}, ${g}, ${b})`;
		} catch (error) {
			return '#000000'; // 采样失败，默认黑色
		}
	},

	/**
	 * 根据背景色计算高对比度文本色（改进版）- 缓存版本
	 * @param {string} bgColor - 背景色（rgb或hex格式）
	 * @returns {string} 高对比度文本色
	 */
	getHighContrastColor: function (bgColor) {
		// 如果手动指定了文本颜色，直接返回
		if (this.config.fallbackTextColor) {
			return this.config.fallbackTextColor;
		}

		// 如果已经计算过且背景色相同，返回缓存
		if (this.cachedTextColor && this.cachedBackgroundColor === bgColor) {
			return this.cachedTextColor;
		}

		// 解析RGB值
		let red, green, blue;

		if (bgColor.startsWith('#')) {
			// 处理十六进制颜色
			let hex = bgColor.slice(1);
			if (hex.length === 3) {
				hex = hex.split('').map(char => char + char).join('');
			}
			red = parseInt(hex.substring(0, 2), 16);
			green = parseInt(hex.substring(2, 4), 16);
			blue = parseInt(hex.substring(4, 6), 16);
		} else if (bgColor.startsWith('rgb')) {
			// 处理rgb/rgba格式
			const rgbValues = bgColor.match(/\d+/g);
			if (rgbValues && rgbValues.length >= 3) {
				[red, green, blue] = rgbValues.map(Number);
			} else {
				this.cachedTextColor = '#ffffff';
				return '#ffffff'; // 解析失败，默认白色
			}
		} else {
			// 处理命名颜色或其他格式
			const testDiv = document.createElement('div');
			testDiv.style.color = bgColor;
			document.body.appendChild(testDiv);
			const computedColor = window.getComputedStyle(testDiv).color;
			document.body.removeChild(testDiv);

			if (computedColor.startsWith('rgb')) {
				const rgbValues = computedColor.match(/\d+/g);
				if (rgbValues && rgbValues.length >= 3) {
					[red, green, blue] = rgbValues.map(Number);
				} else {
					this.cachedTextColor = '#ffffff';
					return '#ffffff';
				}
			} else {
				this.cachedTextColor = '#ffffff';
				return '#ffffff';
			}
		}

		// 使用WCAG 2.1标准计算相对亮度
		const gamma = (c) => {
			c = c / 255;
			return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
		};

		const luminance = 0.2126 * gamma(red) + 0.7152 * gamma(green) + 0.0722 * gamma(blue);

		// 根据亮度选择对比色，阈值调整为0.179（更好的对比效果）
		const textColor = luminance > 0.179 ? '#000000' : '#ffffff';

		// 缓存结果
		this.cachedTextColor = textColor;
		return textColor;
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
			'zh-CN': { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' },
			'en-US': { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' },
			'ja-JP': { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' },
			'de-DE': { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }
		};

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
			hours = hours || 12;
		}

		// 基础时间字符串
		let timeString = `${hours}:${minutes}`;

		// 添加秒数
		if (this.config.displaySeconds) {
			timeString += `:${seconds}`;
		}

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
				dateElement.className = "date normal medium fade-animation active";
				dateElement.textContent = this.formatDateByLanguage(displayDate);
				dateElement.style.transition = "opacity 1s ease-in-out";
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
		// if (this.config.displayType !== "digital") {
		// 	const analogContainer = document.createElement("div");
		// 	analogContainer.className = "clock-circle";
		// 	analogContainer.style.width = this.config.analogSize;
		// 	analogContainer.style.height = this.config.analogSize;

		// 	// 设置表盘样式
		// 	if (this.config.analogFace && this.config.analogFace !== "simple" && this.config.analogFace !== "none") {
		// 		analogContainer.style.background = `url(${this.data.path}faces/${this.config.analogFace}.svg)`;
		// 		analogContainer.style.backgroundSize = "100%";
		// 		analogContainer.style.border = "rgba(0, 0, 0, 0.1)";
		// 	} else if (this.config.analogFace !== "none") {
		// 		analogContainer.style.border = "2px solid";
		// 	}

		// 	// 时钟面板
		// 	const clockFace = document.createElement("div");
		// 	clockFace.className = "clock-face";

		// 	// 时针
		// 	const hours = displayDate.getHours() % 12;
		// 	const minutes = displayDate.getMinutes();
		// 	const hourDegrees = (hours * 30) + (minutes * 0.5) + 90;
		// 	const hourHand = document.createElement("div");
		// 	hourHand.className = "clock-hour";
		// 	hourHand.style.transform = `rotate(${hourDegrees}deg)`;

		// 	// 分针
		// 	const minuteDegrees = (minutes * 6) + 90;
		// 	const minuteHand = document.createElement("div");
		// 	minuteHand.className = "clock-minute";
		// 	minuteHand.style.transform = `rotate(${minuteDegrees}deg)`;

		// 	clockFace.appendChild(hourHand);
		// 	clockFace.appendChild(minuteHand);

		// 	// 秒针
		// 	if (this.config.displaySeconds) {
		// 		const seconds = displayDate.getSeconds();
		// 		const secondDegrees = (seconds * 6) + 90;
		// 		const secondHand = document.createElement("div");
		// 		secondHand.className = "clock-second";
		// 		secondHand.style.transform = `rotate(${secondDegrees}deg)`;
		// 		clockFace.appendChild(secondHand);
		// 	}

		// 	analogContainer.appendChild(clockFace);
		// 	container.appendChild(analogContainer);
		// }

		// 设置布局
		// if (this.config.displayType === "both") {
		// 	container.classList.add(`clock-grid-${this.config.analogPlacement}`);
		// }

		// 改进的颜色检测和应用 - 只在首次或需要时执行
		// if (!this.colorDetectionComplete) {
		// 	setTimeout(() => {
		// 		let bgColor;

		// 		if (this.config.autoDetectBackground) {
		// 			bgColor = this.getActualBackgroundColor(container);
		// 		} else {
		// 			bgColor = '#000000'; // 默认黑色背景
		// 		}

		// 		const textColor = this.getHighContrastColor(bgColor);
		// 		console.log("最终背景色:", bgColor, "文本色:", textColor);


		// 		// 标记颜色检测完成
		// 		this.colorDetectionComplete = true;
		// 	}, 100);
		// }

		return container;
	},

});
