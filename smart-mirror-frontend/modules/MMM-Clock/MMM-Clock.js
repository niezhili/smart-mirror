Module.register("MMM-Clock", {
defaults: {
displayType: "digital",
language: config.language,
timezone: null,
timeFormat: 24,
displaySeconds: false,
showPeriod: true,
showPeriodUpper: false,
clockBold: false,
showDate: true,
analogFace: "simple",
analogSize: "200px",
analogPlacement: "bottom",
dateFormat: "default",
showWeek: false,
compactDate: false
},

getStyles: function() {
return ["customclock.css"];
},

start: function() {
Log.info(`Starting module: ${this.name}`);
this.scheduleTick();
},

scheduleTick: function() {
	// 按分钟边界刷新，避免持续重绘导致时钟区域闪烁。
	const delay = this.config.displaySeconds ? 1000 : (60 - new Date().getSeconds()) * 1000;
clearTimeout(this.refreshTimer);
this.refreshTimer = setTimeout(() => {
this.updateDom(0);
this.scheduleTick();
}, delay);
},

getLocale: function() {
const mapping = {
en: "en-US",
"zh-cn": "zh-CN",
fr: "fr-FR",
ja: "ja-JP",
ko: "ko-KR",
es: "es-ES"
};

return mapping[String(config.language || this.config.language || "en").toLowerCase()] || "en-US";
},

resolveDisplayDate: function() {
const now = new Date();
if (!this.config.timezone) {
return now;
}

// 使用 Intl 在目标时区格式化后再回构日期，避免本地时区干扰展示结果。
const locale = this.getLocale();
const parts = new Intl.DateTimeFormat(locale, {
timeZone: this.config.timezone,
year: "numeric",
month: "2-digit",
day: "2-digit",
hour: "2-digit",
minute: "2-digit",
second: "2-digit",
hour12: false
}).formatToParts(now);
const values = Object.fromEntries(parts.filter((item) => item.type !== "literal").map((item) => [item.type, item.value]));
return new Date(`${values.year}-${values.month}-${values.day}T${values.hour}:${values.minute}:${values.second}`);
},

formatDateByLanguage: function(date) {
const locale = this.getLocale();
const options = this.config.compactDate
? { month: "short", day: "numeric", weekday: "short" }
: { weekday: "long", month: "long", day: "numeric", year: "numeric" };
return date.toLocaleDateString(locale, options);
},

formatWeekLabel: function(date) {
const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
const pastDays = (date - firstDayOfYear) / 86400000;
const weekNumber = Math.ceil((pastDays + firstDayOfYear.getDay() + 1) / 7);
return this.translate("WEEK", { weekNumber }, `Week ${weekNumber}`);
},

resolveDayPeriod: function(date) {
const locale = this.getLocale();
const parts = new Intl.DateTimeFormat(locale, {
hour: "numeric",
hour12: true
}).formatToParts(date);
const dayPeriod = parts.find((item) => item.type === "dayPeriod");

if (!dayPeriod) {
	return date.getHours() >= 12 ? "PM" : "AM";
}

return this.config.showPeriodUpper ? dayPeriod.value.toUpperCase() : dayPeriod.value.toLowerCase();
},

formatTimeParts: function(date) {
let hours = date.getHours();
const minutes = String(date.getMinutes()).padStart(2, "0");
const seconds = String(date.getSeconds()).padStart(2, "0");
let period = "";

if (this.config.timeFormat !== 24) {
period = this.resolveDayPeriod(date);
hours = hours % 12 || 12;
}

return {
hours: String(hours).padStart(2, "0"),
minutes,
seconds,
period
};
},

buildDigitalClock: function(displayDate) {
const digitalContainer = document.createElement("div");
digitalContainer.className = "digital glass-clock";

if (this.config.showDate) {
const dateElement = document.createElement("div");
dateElement.className = "clock-date";
dateElement.textContent = this.formatDateByLanguage(displayDate);
digitalContainer.appendChild(dateElement);
}

const timeParts = this.formatTimeParts(displayDate);
const timeShell = document.createElement("div");
timeShell.className = `clock-face-digital${this.config.clockBold ? " is-bold" : ""}`;

const hoursElement = document.createElement("span");
hoursElement.className = "clock-hours";
hoursElement.textContent = timeParts.hours;
timeShell.appendChild(hoursElement);

const colonElement = document.createElement("span");
colonElement.className = "clock-colon";
colonElement.textContent = ":";
timeShell.appendChild(colonElement);

const minutesElement = document.createElement("span");
minutesElement.className = "clock-minutes";
minutesElement.textContent = timeParts.minutes;
timeShell.appendChild(minutesElement);

if (this.config.displaySeconds) {
	const secondsElement = document.createElement("span");
	secondsElement.className = "clock-period";
	secondsElement.textContent = timeParts.seconds;
	timeShell.appendChild(secondsElement);
}

if (this.config.timeFormat !== 24 && this.config.showPeriod) {
const periodElement = document.createElement("span");
periodElement.className = "clock-period";
periodElement.textContent = timeParts.period;
timeShell.appendChild(periodElement);
}

digitalContainer.appendChild(timeShell);

if (this.config.showWeek) {
const weekElement = document.createElement("div");
weekElement.className = "clock-week";
weekElement.textContent = this.formatWeekLabel(displayDate);
digitalContainer.appendChild(weekElement);
}

return digitalContainer;
},

buildAnalogClock: function(displayDate) {
const analogContainer = document.createElement("div");
analogContainer.className = "clock-circle";
analogContainer.style.width = this.config.analogSize;
analogContainer.style.height = this.config.analogSize;

const clockFace = document.createElement("div");
clockFace.className = "clock-face";
analogContainer.appendChild(clockFace);

const hourHand = document.createElement("div");
hourHand.className = "clock-hour";
const minuteHand = document.createElement("div");
minuteHand.className = "clock-minute";
clockFace.appendChild(hourHand);
clockFace.appendChild(minuteHand);

const hours = displayDate.getHours() % 12;
const minutes = displayDate.getMinutes();
hourHand.style.transform = `rotate(${(hours * 30) + (minutes * 0.5) + 90}deg)`;
minuteHand.style.transform = `rotate(${(minutes * 6) + 90}deg)`;

return analogContainer;
},

getDom: function() {
const container = document.createElement("div");
container.className = "customclock-grid";
const displayDate = this.resolveDisplayDate();

if (this.config.displayType !== "analog") {
container.appendChild(this.buildDigitalClock(displayDate));
}

if (this.config.displayType !== "digital") {
container.appendChild(this.buildAnalogClock(displayDate));
}

if (this.config.displayType === "both") {
container.classList.add(`clock-grid-${this.config.analogPlacement}`);
}

return container;
},

stop: function() {
clearTimeout(this.refreshTimer);
}
});

