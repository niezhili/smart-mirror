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
	languageState = require('./modules/MMM-LanguageSwitch/language-state.js');
} catch (e) {
	// Default to English if module not installed
	languageState = { getLanguage: () => "En-us" };
}

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

	language: languageState.getLanguage(),
	locale: languageState.getLanguage(),

	//
    // language: "En-us",
    // locale: "EN-US",

	 // 添加 "DEBUG" 以获取更多日志
		timeFormat: 24,
		units: "公制",

		modules: [
		{
			module: "MMM-CustomClock",
			position: "top_center", // Or wherever you had your clock
			config: {
				timeFormat: 24, // Use 12 or 24
				displayType: "digital", // "digital", "analog", or "both"
				showDate: true,
				displaySeconds: true
				// Add any other options you want to customize
			}
		},
		{
        module: "MMM-CalligraphyButton", // 模块名称（要和模块文件夹名一致）
        position: "top_left", // 按钮显示的位置（如 top_left、bottom_center 等）
        config: {
            buttonText: "生成书法作品", // 自定义按钮文字（可选，也可留空用模块默认值）
            targetPage: "calligraphy.html" // 二级界面的HTML路径（需确保文件存在）
        	}
    	},
			{
				module: "MMM-LanguageSwitch",
				position: "bottom_right",
				config: {
					language: "en"
				}
			},
		{
			module: "MMM-CustomWeather",
			position: "top_left",
			config: {
				apiKey: "8ff8d7c3dd9d4e3190df3931536544ef",
				debug: true,
				updateInterval: 60000
			}
		},
		{

			module: "MMM-DHT11",
			position: "bottom_left",
			config:{
			   sensorPin:4, 
			   updateInterval: 1000,
			   temperatureUnit: "C"
			}
		},
		{
			module: "MMM-BackgroundImage",
			position: "fullscreen_below",
			config: {
				bgName: "red-bg-image.png",
				videoName: "",
				height: "100%",
				width: "100%",
			}
		},

		// {
		// 	module: 'MMM-Clockinese',
		// 	position: 'top_center',
		// 	config: {
		// 	  timeZone: "n33", // See timeZone chart below for your timeZone code
		// 	  language: "en"
		// 	}
	 	// },
		{
			module: "MMM-NewsScroller",
			position: "top_right",  // Choose a position that works for your setup
			config: {
				//API key and URL are already set in the defaults, but you can override them here if needed
				apiUrl: "https://v.juhe.cn/toutiao/index", // Using HTTPS
				apiKey: "7268a1f3d036719920a9bff93ca6b6b1",
				newsType: "guoji"
			}
		},
		{
//			header: "月历",
			module: "MMM-MonthlyCalendar",
			position: "bottom_center",
			config: { // See "Configuration options" for more information.
			mode: "fourWeeks",
			firstDayOfWeek: "Sunday",
			multiDayEndingTimeSeparator: "至",
			}
		},
		{
			module: "MMM-quotes",
			position: "lower_third",
			config: {
				updateInterval: 30000,
				fadeSpeed: 1000,
				authorAlign: "align-right",
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
