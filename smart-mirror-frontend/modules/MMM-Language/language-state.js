const fs = require("fs");
const path = require("path");

const stateFilePath = path.resolve(__dirname, "language-state.json");

function normalizeLanguage(language) {
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
}

if (!fs.existsSync(stateFilePath)) {
fs.writeFileSync(stateFilePath, JSON.stringify({ language: "en" }, null, 2));
}

module.exports = {
getLanguage: function() {
const data = JSON.parse(fs.readFileSync(stateFilePath, "utf8"));
return normalizeLanguage(data.language);
},

setLanguage: function(language) {
fs.writeFileSync(stateFilePath, JSON.stringify({ language: normalizeLanguage(language) }, null, 2));
}
};
