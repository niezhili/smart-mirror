'use strict';
/* global Log, Module, JSON */

/* Magic Mirror
 * Module: Compliments
 *
 * By Michael Teeuw http://michaelteeuw.nl
 * MIT Licensed.
 */

Module.register('MMM-quotes',{

	// Module config defaults.
	defaults: {
		quotes: [
			{
				quote: 'If you can dream it, you can do it.', 
				zh: '只要敢梦想，就能实现。', 
				author: 'Walt Disney'
			},
			{
				quote: 'No matter how slow you go, you are still lapping everybody on the couch.',
				zh: '无论你走得多慢，你都比躺在沙发上的人进步。',
				author: 'Unknown'
			},
			{
				quote: 'Don\'t cry because it\'s over. Smile because it happened.',
				zh: '不要为结束而哭泣，要为曾经发生而微笑。',
				author: 'Dr. Seuss'
			},
			{
				quote: 'It\'s kind of fun to do the impossible.',
				zh: '做不可能的事，其实挺有趣的。',
				author: 'Walt Disney'
			},
			{
				quote: 'A person\'s a person, no matter how small.',
				zh: '人就是人，无论多么渺小。',
				author: 'Dr. Seuss'
			},
			{
				quote: 'The way to get started is to quit talking and begin doing.',
				zh: '开始的方法就是停止空谈，立即行动。',
				author: 'Walt Disney'
			},
			{
				quote: 'I like nonsense; it wakes up the brain cells.',
				zh: '我喜欢无稽之谈，它能唤醒脑细胞。',
				author: 'Dr. Seuss'
			},
			{
				quote: 'Do not dwell in the past, do not dream of the future, concentrate the mind on the present moment.',
				zh: '不沉溺过去，不空想未来，专注当下。',
				author: 'Budha'
			},
			{
				quote: 'What we think, we become.',
				zh: '我们想什么，就会成为什么。',
				author: 'Budha'
			},
			{
				quote: 'It does not matter how slowly you go as long as you do not stop.',
				zh: '只要不停步，走多慢都没关系。',
				author: 'Confucius'
			},
			{
				quote: 'You can not open a book without learning something.',
				zh: '开卷有益。',
				author: '《论语》'
			},
			{
				quote: 'Attitude is a little thing that makes a big difference.',
				zh: '态度虽小，影响巨大。',
				author: 'Winston Churchill'
			},
			{
				quote: '人道洛阳花似锦，偏我来时不逢春', 
				en: 'People say Luoyang is full of flowers like brocade, but when I came, spring was gone.', 
				author: '刘过《唐多令·芦叶满汀州》'
			},
			{
				quote: "蓦然回首，那人却在，灯火阑珊处",
				en: 'Suddenly looking back, that person is there, where the lights are dim.',
				author: "辛弃疾《青玉案·元夕》"
			},
			{
				quote: "人生到处知何似，应似飞鸿踏雪泥",
				en: 'What is life like everywhere? It should be like a swan stepping on snow mud.',
				author: "苏轼《和子由渑池怀旧》"
			},
			{
				quote: "去留无意，漫随天外云卷云舒",
				en: 'Unconcerned about staying or leaving, just follow the clouds rolling and unfolding beyond the sky.',
				author: "洪应明《菜根谭》"
			},
			{
				quote: "桥如虹，水如空，一叶飘然烟雨中",
				en: 'The bridge is like a rainbow, the water is like the sky, a leaf drifts in the misty rain.',
				author: "陆游《鹊桥仙·华灯纵博》"
			},
			{
				quote: "愿作深山木，枝枝连理生",
				en: 'I wish to be a tree in the deep mountains, with branches growing together.',
				author: "白居易《长相思》"
			},
			{
				quote: "握笔别僵!食指拇指轻捏笔杆，掌心留小空隙，运笔才不“卡壳”~",
				en: 'Don\'t hold the pen stiffly! Pinch the pen lightly with your index finger and thumb, leave a small gap in your palm, so the pen won\'t "jam"~',
				author: "佚名"
			},
			{
				quote: "新手练笔选熟宣/半熟宣，生宣太洇墨，容易写“糊”哦~",
				en: 'Beginners can choose between seasoned paper or semi-seasoned paper for practice, as the unseasoned paper absorbs ink easily and can lead to messy writing~',
				author: "佚名"
			},
			{
				quote: "永字八法：点侧横勒竖弩钩趯，八笔拆解楷书筋骨",
				en: 'The Eight Principles of "Yong": Dot, Side, Horizontal, Rein, Vertical, Bow, Hook, Tiao - eight strokes to disassemble the bones of regular script.',
				author: "佚名"
			},
			{
				quote: "碑帖之别：碑刻纪事显庄重，帖拓墨迹传笔法，临习各有其妙。",
				en: 'Difference between steles and calligraphy copies: Steles record events and appear solemn; copies pass on brushwork techniques. Practicing each has its own wonders.',
				author: "佚名"
			},
			{
				quote: "篆书工具：篆书宜用中锋笔，线条圆润显古朴，藏锋起收更稳当。",
				en: 'Seal script tools: Seal script should use a center-tip brush, with round lines showing simplicity; hiding the tip when starting and ending is more stable.',
				author: "佚名"
			}
		],
		updateInterval: 30000,
		fadeSpeed: 4000
	},

	// Define required scripts.
	getStyles: function() {
		return ['MMM-quotes.css'];
	},

	// 初始化当前语言（与其他模块同步）
	start: function() {
		Log.info('[QUOTES] Starting module: ' + this.name);

		this.lastQuoteIndex = -1;
		// 从localStorage获取当前语言
		this.currentLanguage = localStorage.getItem("mm_language") || config.language;
		// 保存当前显示的句子索引（初始为null，首次加载会随机）
		this.currentQuoteIndex = null;

		// Schedule update timer.
		var self = this;
		setInterval(function() {
			// 定时刷新时，重置当前索引（允许下次随机新句子）
			self.currentQuoteIndex = null;
			self.updateDom(self.config.fadeSpeed);
		}, this.config.updateInterval);
	},

	// 监听器
	notificationReceived: function(notification, payload) {
		if (notification === "LANGUAGE_CHANGED") {
			Log.info(`[MMM-quotes] 收到语言切换通知，新语言: ${payload}`);
			this.currentLanguage = payload; // 更新当前语言
			this.updateDom(this.config.fadeSpeed); // 刷新显示对应语言的名言（不重置索引，保持原句）
		}
	},

	/* randomIndex(quotes)
	 * Generate a random index for a list of quotes.
	 *
	 * argument quotes Array<Object> - Array with quotes.
	 *
	 * return Number - Random index.
	 */
	randomIndex: function(quotes) {
		if (quotes.length === 1) {
			return 0;
		}

		var generate = function() {
			return Math.floor(Math.random() * quotes.length);
		};

		var quoteIndex = generate();

		while (quoteIndex === this.lastQuoteIndex) {
			quoteIndex = generate();
		}

		this.lastQuoteIndex = quoteIndex;

		return quoteIndex;
	},

	/* randomQuote()（返回对应语言的名言）
	 * Retrieve a random quote.
	 *
	 * return quote object - A quote with attribution.
	 */
	randomQuote: function() {
    Log.info('[QUOTES] Entering randomQuote()');
		// 如果有当前索引（语言切换时），直接复用；否则随机新索引
		var index = this.currentQuoteIndex !== null ? this.currentQuoteIndex : this.randomIndex(this.config.quotes);
		// 保存当前索引（下次语言切换时复用）
		this.currentQuoteIndex = index;
    Log.info('[QUOTES] current index: ' + index.toString());

		var originalQuote = this.config.quotes[index];
		// 根据当前语言返回对应翻译（优先用多语言字段，没有则用原有quote字段）
		return {
			// 语言为中文（Zh-cn）→ 用zh字段，否则用en字段，都没有则用原quote
			text: this.currentLanguage.toLowerCase() === "zh-cn" 
				? (originalQuote.zh || originalQuote.quote) 
				: (originalQuote.en || originalQuote.quote),
			author: originalQuote.author
		};
	},

	// Override dom generator.（显示对应语言的文本）
	getDom: function() {
    Log.info('[QUOTES] Entering getDom()');
		var quoteObj = this.randomQuote(); // 现在返回的是带对应语言text的对象

    Log.info('[QUOTES] quoteObj: ' + quoteObj.text.toString());

		var wrapper = document.createElement('div');
    var quoteWrapper = document.createElement('div');
    var authorWrapper = document.createElement('div');
		quoteWrapper.className = 'quotes medium bright light';
    authorWrapper.className = 'quotes quotes-author thin small bright';

    quoteWrapper.innerHTML = quoteObj.text; // 显示对应语言的文本（原先是quoteObj.quote）
    authorWrapper.innerHTML = '—' + quoteObj.author;
		wrapper.appendChild(quoteWrapper);
    wrapper.appendChild(authorWrapper);


		return wrapper;
	},
	

});
