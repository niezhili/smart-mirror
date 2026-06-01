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
				module: "MMM-CustomWeather",
				position: "top_left",
				config: {
					apiKey: "8ff8d7c3dd9d4e3190df3931536544ef",
					debug: true,
					// updateInterval: 60000
				}
			}
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
