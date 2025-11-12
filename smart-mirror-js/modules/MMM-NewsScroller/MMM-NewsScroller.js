Module.register("MMM-NewsScroller", {
	// Default module config
	defaults: {
		updateInterval: 5000, // 滚动间隔（毫秒）
		apiUrl: "https://v.juhe.cn/toutiao/index", // 固定新闻API地址
		apiKey: "7268a1f3d036719920a9bff93ca6b6b1", // 新闻API密钥
		newsType: "guoji", // 固定新闻类型（不随语言变）
		updateSchedule: [
			{ hour: 5, minute: 0 },
			{ hour: 7, minute: 0 },
			{ hour: 11, minute: 0 },
			{ hour: 12, minute: 0 },
			{ hour: 14, minute: 0 },
			{ hour: 15, minute: 0 },
			{ hour: 17, minute: 0 },
			{ hour: 19, minute: 0 },
			{ hour: 23, minute: 0 }
		],
		maxNewsItems: 10,
		showSourceInfo: true,
		useNodeFetch: true, // 必须通过node_helper请求（翻译需后端转发）
		enableTranslation: true, // 启用翻译（核心开关）
		baiduAppId: "20250407002326273", // 百度翻译API AppId
		baiduSecretKey: "Srd_2lNeita_aL09ML6q", // 百度翻译API密钥
		defaultLanguage: "Zh-cn" // 默认语言
	},

	// 模块内部状态（保存当前显示的新闻索引）
	state: {
		rawNewsItems: [], // 原始新闻数据（未翻译，固定不变）
		translatedNewsItems: [], // 翻译后的新闻数据
		activeItem: 0,
		loaded: false,
		currentLanguage: null, // 当前语言（同步MMM-LanguageSwitch）
		// 锁定当前显示的新闻索引（语言切换时保持）
		lockedActiveItem: null 
	},

	// 加载样式
	getStyles: function() {
		return ["MMM-NewsScroller.css"];
	},

	// 模块启动初始化
	start: function() {
		Log.info("Starting module: " + this.name);

		// 1. 初始化当前语言（优先读取MMM-LanguageSwitch保存的状态）
		this.state.currentLanguage = localStorage.getItem("mm_language") || this.config.defaultLanguage;

		// 2. 注册并初始化node_helper
		this.sendSocketNotification("INIT", {
			config: this.config,
			currentLanguage: this.state.currentLanguage
		});

		// 3. 首次拉取新闻（固定数据源）
		this.fetchRawNews();

		// 4. 启动定时任务（滚动+新闻更新）
		this.scheduleNextNewsUpdate();
		this.scheduleScroll();
	},

	// 拉取原始新闻（固定数据源，不随语言变）
	fetchRawNews: function() {
		Log.info("MMM-NewsScroller: Fetching raw news...");

		if (this.config.useNodeFetch) {
			// 通过node_helper拉取新闻（避免前端跨域）
			this.sendSocketNotification("FETCH_RAW_NEWS", {
				url: this.config.apiUrl,
				key: this.config.apiKey,
				type: this.config.newsType
			});
		} else {
			Log.error("MMM-NewsScroller: 必须启用useNodeFetch，否则无法安全调用翻译API");
		}
	},

	// 处理原始新闻数据（拉取后立即触发翻译）
	processRawNews: function(rawData) {
		if (rawData && rawData.result && rawData.result.data) {
			// 保存原始新闻（不变）
			this.state.rawNewsItems = rawData.result.data.slice(0, this.config.maxNewsItems);
			this.state.loaded = true;

			// 立即触发翻译（根据当前语言）
			this.translateNewsIfNeeded();
		} else {
			Log.error("MMM-NewsScroller: 原始新闻数据格式错误", rawData);
		}
	},

	// 根据当前语言翻译新闻（如果启用翻译）
	translateNewsIfNeeded: function() {
		// 若未启用翻译，直接使用原始数据
		if (!this.config.enableTranslation) {
			this.state.translatedNewsItems = [...this.state.rawNewsItems];
			this.updateDom(1000);
			return;
		}

		Log.info(`MMM-NewsScroller: 开始翻译新闻（目标语言：${this.state.currentLanguage}）`);

		// 向node_helper发送翻译请求（避免前端暴露密钥）
		this.sendSocketNotification("TRANSLATE_NEWS", {
			rawNews: this.state.rawNewsItems,
			targetLang: this.state.currentLanguage === "Zh-cn" ? "zh" : "en", // 百度API语言码（zh/en）
			appId: this.config.baiduAppId,
			secretKey: this.config.baiduSecretKey
		});
	},

	// 处理翻译结果（修改：恢复锁定的新闻索引）
	processTranslatedNews: function(translatedData) {
		if (translatedData && translatedData.length > 0) {
			this.state.translatedNewsItems = translatedData;
			Log.info("MMM-NewsScroller: 新闻翻译完成");

			// 如果有锁定的索引，恢复到该索引（语言切换时保持原条目）
			if (this.state.lockedActiveItem !== null) {
				this.state.activeItem = this.state.lockedActiveItem;
				// 解锁（仅在语言切换时临时锁定）
				this.state.lockedActiveItem = null;
			}

			this.updateDom(1000); // 刷新界面显示翻译后内容
		} else {
			Log.error("MMM-NewsScroller: 翻译结果为空", translatedData);
			// 翻译失败时回退到原始新闻
			this.state.translatedNewsItems = [...this.state.rawNewsItems];
			this.updateDom(1000);
		}
	},

	// 定时滚动新闻
	scheduleScroll: function() {
		setInterval(() => {
			if (this.state.translatedNewsItems.length > 0) {
				this.state.activeItem = (this.state.activeItem + 1) % this.state.translatedNewsItems.length;
				this.updateDom(1000);
			}
		}, this.config.updateInterval);
	},

	// 定时更新原始新闻
	scheduleNextNewsUpdate: function() {
		const now = new Date();
		let nextUpdate = null;
		let earliestTime = null;

		// 查找下一个更新时间点
		for (let schedule of this.config.updateSchedule) {
			const scheduleTime = new Date();
			scheduleTime.setHours(schedule.hour, schedule.minute, 0, 0);

			if (scheduleTime > now && (!nextUpdate || scheduleTime < nextUpdate)) {
				nextUpdate = scheduleTime;
			}
			if (!earliestTime || scheduleTime < earliestTime) {
				earliestTime = scheduleTime;
			}
		}

		// 若当天无更新，顺延到次日
		if (!nextUpdate) {
			nextUpdate = new Date(earliestTime);
			nextUpdate.setDate(nextUpdate.getDate() + 1);
		}

		// 定时触发下一次新闻拉取
		setTimeout(() => {
			this.fetchRawNews();
			this.scheduleNextNewsUpdate();
		}, nextUpdate.getTime() - now.getTime());

		Log.info("MMM-NewsScroller: 下一次新闻更新时间: " + nextUpdate.toLocaleString());
	},

	// 生成界面DOM
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "news-scroller";

		// 加载中状态
		if (!this.state.loaded) {
			wrapper.innerHTML = this.state.currentLanguage === "Zh-cn" ? "加载新闻中..." : "Loading news...";
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		// 无新闻状态
		if (this.state.translatedNewsItems.length === 0) {
			wrapper.innerHTML = this.state.currentLanguage === "Zh-cn" ? "暂无新闻数据" : "No news available.";
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		// 显示当前新闻（翻译后）
		const currentNews = this.state.translatedNewsItems[this.state.activeItem];
		const newsWrapper = document.createElement("div");
		newsWrapper.className = "news-item fade-in";

		// 新闻标题（翻译后）
		const title = document.createElement("div");
		title.className = "news-title bright";
		title.innerHTML = currentNews.translatedTitle || currentNews.title; // 优先显示翻译后标题
		newsWrapper.appendChild(title);

		// 新闻来源信息（日期自动适配语言）
		if (this.config.showSourceInfo) {
			const sourceInfo = document.createElement("div");
			sourceInfo.className = "news-source light small";

			// 日期格式化（根据当前语言自动切换显示格式）
			const newsDate = new Date(currentNews.date);
			const dateString = newsDate.toLocaleDateString(this.state.currentLanguage, {
				day: "numeric",
				month: "short",
				hour: "2-digit",
				minute: "2-digit"
			});

			// 来源信息
			const category = currentNews.translatedCategory || currentNews.category;
			sourceInfo.innerHTML = `${category} • ${currentNews.author_name || "Unknown"} • ${dateString}`;
			newsWrapper.appendChild(sourceInfo);
		}

		wrapper.appendChild(newsWrapper);
		return wrapper;
	},

	/**
	 * 语言切换监听器（锁定当前新闻索引）
	 */
	notificationReceived: function(notification, payload, sender) {
		// 监听MMM-LanguageSwitch发送的语言切换通知
		if (notification === "LANGUAGE_CHANGED") {
			Log.info(`MMM-NewsScroller: 收到语言切换通知，切换为: ${payload}`);

			// 1. 锁定当前显示的新闻索引（记录语言切换前的条目）
			this.state.lockedActiveItem = this.state.activeItem;

			// 2. 更新模块内部当前语言
			this.state.currentLanguage = payload;

			// 3. 重新翻译已有的原始新闻（但会保持锁定的索引）
			this.translateNewsIfNeeded();

			// 4. 刷新界面（更新加载/无数据提示文字、日期格式等）
			this.updateDom(1000);
		}
	},

	/**
	 * 接收node_helper的消息
	 */
	socketNotificationReceived: function(notification, payload) {
		// 原始新闻拉取完成
		if (notification === "RAW_NEWS_RESULT") {
			this.processRawNews(payload);
		}

		// 翻译完成
		if (notification === "TRANSLATED_NEWS_RESULT") {
			this.processTranslatedNews(payload);
		}

		// 错误提示
		if (notification === "ERROR") {
			Log.error("MMM-NewsScroller: node_helper错误:", payload);
		}
	}
});
