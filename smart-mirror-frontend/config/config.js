/* Config Sample
 *
 * For more information on how you can configure this file
 * see https://docs.magicmirror.builders/configuration/introduction.html
 * and https://docs.magicmirror.builders/modules/configuration.html
 *
 * You can use environment variables using a `config.js.template` file instead of `config.js`
 * which will be converted to `config.js` while starting. For more information
 * see https://docs.magicmirror.builders/configuration/introduction.html#enviromnent-variables
 */
let languageState;
try {
	languageState = require("../modules/MMM-Language/language-state.js");
} catch (e) {
	languageState = { getLanguage: () => "en" };
}

function normalizeMirrorLanguage(language) {
	const normalized = String(language || "en").toLowerCase();
	const aliases = {
		"en-us": "en",
		"en-gb": "en",
		zh: "zh-cn",
		"zh_cn": "zh-cn",
		"zh-cn": "zh-cn",
		"zh-hans": "zh-cn",
		"fr-fr": "fr",
		"ja-jp": "ja",
		"ko-kr": "ko",
		"es-es": "es"
	};

	return aliases[normalized] || normalized;
}

function toLocaleCode(language) {
	const mapping = {
		en: "en-US",
		"zh-cn": "zh-CN",
		fr: "fr-FR",
		ja: "ja-JP",
		ko: "ko-KR",
		es: "es-ES"
	};

	return mapping[language] || "en-US";
}

const currentLanguage = normalizeMirrorLanguage(languageState.getLanguage());
const currentLocale = toLocaleCode(currentLanguage);

let config = {
	address: "localhost",	// Address to listen on, can be:
	port: 8080,
	basePath: "/",	// The URL path where MagicMirror² is hosted. If you are using a Reverse proxy

	// ipWhitelist: ["127.0.0.1", "::ffff:127.0.0.1", "::1"],	// Set [] to allow all IP addresses

	useHttps: false,			// Support HTTPS or not, default "false" will use HTTP
	httpsPrivateKey: "",	// HTTPS private key path, only require when useHttps is true
	httpsCertificate: "",	// HTTPS Certificate path, only require when useHttps is true

	// language: "Zh-cn",
    // locale: "zh-cn",

	// Get language from state file
	rateLimitWindowMs: 60 * 1000, // 1分钟
	rateLimitMax: 200, // 每分钟最多50个请求
	ipWhitelist: ["192.168.1.100", "127.0.0.1","192.168.31.50","::ffff:127.0.0.1", "::1"] ,// 白名单IP不受限制

	language: currentLanguage,
	locale: currentLocale,

	//
    // language: "En-us",
    // locale: "EN-US",

	 // 添加 "DEBUG" 以获取更多日志
		timeFormat: 24,
		units: "公制",

		modules: [
		{
			module: "MMM-Clock",
			position: "top_center",
			config: {
				timeFormat: 24,
				displayType: "digital",
				showDate: true,
				displaySeconds: false,
				clockBold: true,
				showWeek: false,
				compactDate: false
			}
		},
		{
			module: "MMM-Language",
			position: "bottom_right",
			config: {
				language: currentLanguage,
				supportedLanguages: [
					{ code: "zh-cn", labelKey: "LANGUAGE_NAME_ZH_CN", shortLabelKey: "LANGUAGE_SHORT_ZH_CN" },
					{ code: "en", labelKey: "LANGUAGE_NAME_EN", shortLabelKey: "LANGUAGE_SHORT_EN" }
				],
				defaultTogglePair: ["zh-cn", "en"],
				longPressDuration: 550
			}
		},
		{
			module: "MMM-Weather",
			position: "top_left",
			config: {
				apiKey: "8ff8d7c3dd9d4e3190df3931536544ef",
				width: "240px",
				height: "auto",
				city: "Hangzhou"
			}
		},
		// {
		// 	module: "MMM-DHT11",
		// 	position: "bottom_left",
		// 	config:{
		// 	   sensorPin:4,
		// 	   updateInterval: 500,
		// 	   temperatureUnit: "C"
		// 	}
		// },
		{
			module: "MMM-Background",
			position: "fullscreen_below",
			config: {
				height: "100%",
				width: "100%",
				overlayOpacity: 0.42,
				themeSampleSize: 48,
				swipeThreshold: 70
			}
		},

	
		{
			module: "MMM-News",
			position: "top_right",
			config: {
				apiUrl: "https://v.juhe.cn/toutiao/index",
				apiKey: "7268a1f3d036719920a9bff93ca6b6b1",
				newsType: "guoji",
				maxNewsItems: 10,
				panelTitleKey: "PANEL_TITLE",
				panelHeight: 520,
				categories: [
					{ key: "top", labelKey: "CATEGORY_TOP" },
					{ key: "guonei", labelKey: "CATEGORY_GUONEI" },
					{ key: "tiyu", labelKey: "CATEGORY_TIYU" },
					{ key: "keji", labelKey: "CATEGORY_KEJI" },
					{ key: "guoji", labelKey: "CATEGORY_GUOJI" }
				]
			}
		},
		{
			module: "MMM-Quote",
			position: "bottom_left",
			config: {
				updateInterval: 16000,
				fadeSpeed: 1000,
				authorAlign: "align-right",
				defaultCategory: "famous",
				categories: [
					{ key: "famous", dataCategory: "名人经典语录", labelKey: "CATEGORY_FAMOUS" },
					{ key: "proverb", dataCategory: "谚语", labelKey: "CATEGORY_PROVERB" },
					{ key: "literature", dataCategory: "文学", labelKey: "CATEGORY_LITERATURE" }
				]
			}
		},
		{
			module: "MMM-Calendar",
			position: "bottom_center",
			config: {
				mode: "fourWeeks",
				firstDayOfWeek: "Sunday"
			}
		},

	],

	electronOptions: {
		webPreferences: {
			nodeIntegration: true,
			enableRemoteModule: true
		}
	},

	paths: {
		fonts: 'fonts'
	}
};

/*************** DO NOT EDIT THE LINE BELOW ***************/
if (typeof module !== "undefined") { module.exports = config; }
