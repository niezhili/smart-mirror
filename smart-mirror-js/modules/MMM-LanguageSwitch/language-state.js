// language-state.js
const fs = require('fs');
const path = require('path');

const stateFilePath = path.resolve(__dirname, 'language-state.json');

// Initialize if doesn't exist
if (!fs.existsSync(stateFilePath)) {
	fs.writeFileSync(stateFilePath, JSON.stringify({ language: "En-us" }));
}

module.exports = {
	getLanguage: function() {
		const data = JSON.parse(fs.readFileSync(stateFilePath, 'utf8'));
		return data.language;
	},

	setLanguage: function(lang) {
		fs.writeFileSync(stateFilePath, JSON.stringify({ language: lang }));
	}
};
