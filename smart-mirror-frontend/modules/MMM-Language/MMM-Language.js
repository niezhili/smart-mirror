Module.register("MMM-Language", {
	defaults: {
		language: "en",
		supportedLanguages: [
			{ code: "zh-cn", label: "涓枃", shortLabel: "涓? },
			{ code: "en", label: "English", shortLabel: "EN" }
		],
		defaultTogglePair: ["zh-cn", "en"],
		longPressDuration: 550
	},

getStyles: function() {
return ["MMM-Language.css"];
},

start: function() {
this.longPressTimer = null;
this.menuOpen = false;
this.ignoreClick = false;
this.currentLanguage = this.normalizeLanguage(localStorage.getItem("mm_language") || this.config.language);
config.language = this.currentLanguage;
config.locale = this.toLocaleCode(this.currentLanguage);
Log.info(`Starting module: ${this.name} with language: ${this.currentLanguage}`);
},

normalizeLanguage: function(language) {
const aliases = {
"en-us": "en",
"en-gb": "en",
"zh": "zh-cn",
"zh_cn": "zh-cn",
"zh-hans": "zh-cn",
"fr-fr": "fr",
"ja-jp": "ja",
"ko-kr": "ko",
"es-es": "es"
};
const normalized = String(language || "en").toLowerCase();
return aliases[normalized] || normalized;
},

toLocaleCode: function(language) {
const locales = {
en: "en-US",
"zh-cn": "zh-CN",
fr: "fr-FR",
ja: "ja-JP",
ko: "ko-KR",
es: "es-ES"
};
return locales[language] || "en-US";
},

getLanguageInfo: function(code) {
return this.config.supportedLanguages.find((item) => item.code === code) || this.config.supportedLanguages[0];
},

persistLanguage: function(language) {
const normalized = this.normalizeLanguage(language);
this.currentLanguage = normalized;
localStorage.setItem("mm_language", normalized);
config.language = normalized;
config.locale = this.toLocaleCode(normalized);
this.sendSocketNotification("SET_LANGUAGE", normalized);
window.location.reload();
},

toggleLanguage: function() {
const [first, second] = this.config.defaultTogglePair.map((item) => this.normalizeLanguage(item));
const nextLanguage = this.currentLanguage === first ? second : first;
this.persistLanguage(nextLanguage);
},

toggleMenu: function(openState) {
this.menuOpen = typeof openState === "boolean" ? openState : !this.menuOpen;
this.updateDom(200);
},

handlePressStart: function() {
clearTimeout(this.longPressTimer);
this.ignoreClick = false;
this.longPressTimer = setTimeout(() => {
this.ignoreClick = true;
this.toggleMenu(true);
}, this.config.longPressDuration);
},

handlePressEnd: function() {
clearTimeout(this.longPressTimer);
},

getDom: function() {
const wrapper = document.createElement("div");
wrapper.className = "language-switch";

const button = document.createElement("button");
button.className = "language-toggle-btn";
button.type = "button";
button.addEventListener("pointerdown", () => this.handlePressStart());
button.addEventListener("pointerup", () => this.handlePressEnd());
button.addEventListener("pointerleave", () => this.handlePressEnd());
button.addEventListener("click", () => {
if (this.ignoreClick) {
this.ignoreClick = false;
return;
}
this.toggleLanguage();
});

const currentLanguage = this.getLanguageInfo(this.currentLanguage);
button.innerHTML = `<span class="language-toggle-short">${currentLanguage.shortLabel || currentLanguage.label}</span><span class="language-toggle-label">${currentLanguage.label}</span>`;
wrapper.appendChild(button);

if (this.menuOpen) {
const panel = document.createElement("div");
panel.className = "language-menu";

this.config.supportedLanguages.forEach((language) => {
const option = document.createElement("button");
option.type = "button";
option.className = `language-option${language.code === this.currentLanguage ? " is-active" : ""}`;
option.textContent = language.label;
option.addEventListener("click", () => this.persistLanguage(language.code));
panel.appendChild(option);
});

wrapper.appendChild(panel);
}

return wrapper;
}
});

