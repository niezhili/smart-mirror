Module.register("MMM-Background", {
defaults: {
height: "100vh",
width: "100vw",
animationSpeed: 600,
updateInterval: 60 * 60 * 1000,
overlayOpacity: 0.42,
themeSampleSize: 48,
swipeThreshold: 70
},

start: function() {
this.wallpapers = [];
this.currentIndex = 0;
this.activeWallpaper = null;
this.fallbackWallpapers = [
"modules/MMM-Background/images/cultures/cha.png",
"modules/MMM-Background/images/cultures/greatwall.png",
"modules/MMM-Background/images/cultures/panda.png"
];
this.pointerStart = null;
this.boundPointerDown = this.handlePointerDown.bind(this);
this.boundPointerUp = this.handlePointerUp.bind(this);
this.retryTimer = null;

this.attachGlobalSwipe();
this.requestWallpapers();
this.showFallbackIfNeeded();
this.interval = setInterval(() => {
this.requestWallpapers();
}, this.config.updateInterval);
},

getStyles: function() {
return ["MMM-Background.css"];
},

getDom: function() {
const wrapper = document.createElement("div");
wrapper.className = "background-stage";
wrapper.style.setProperty("--background-overlay-opacity", this.config.overlayOpacity);
if (this.activeWallpaper) {
wrapper.style.backgroundImage = `url("${this.activeWallpaper}")`;
wrapper.style.backgroundSize = "cover";
wrapper.style.backgroundPosition = "center";
}

if (this.activeWallpaper) {
const image = document.createElement("img");
image.className = "photo";
image.src = this.activeWallpaper;
image.alt = "Background image";
wrapper.appendChild(image);
}

const overlay = document.createElement("div");
overlay.className = "background-overlay";
wrapper.appendChild(overlay);

const glow = document.createElement("div");
glow.className = "background-glow";
wrapper.appendChild(glow);

return wrapper;
},

getCurrentDateInfo: function() {
const now = new Date();
const month = String(now.getMonth() + 1).padStart(2, "0");
const day = String(now.getDate()).padStart(2, "0");
return {
dateString: `${month}-${day}`
};
},

requestWallpapers: function() {
const dateInfo = this.getCurrentDateInfo();
this.sendSocketNotification("GET_WALLPAPER_COLLECTION", {
dateString: dateInfo.dateString,
modulePath: this.data.path
});
},

socketNotificationReceived: function(notification, payload) {
if (notification !== "WALLPAPER_COLLECTION" || !payload || !Array.isArray(payload.images)) {
return;
}

if (!payload.images.length) {
// 鍚姩闃舵濡傛灉鏆傛椂鎷夸笉鍒板浘鐗囷紝鐭棿闅旈噸璇曪紝閬垮厤绛夊緟鍒颁笅涓€涓皬鏃躲€?clearTimeout(this.retryTimer);
this.retryTimer = setTimeout(() => {
this.requestWallpapers();
}, 15000);
this.wallpapers = [...this.fallbackWallpapers];
this.currentIndex = 0;
this.showWallpaper(this.currentIndex, true);
return;
}

this.wallpapers = payload.images;
this.currentIndex = Math.max(0, Math.min(payload.initialIndex || 0, this.wallpapers.length - 1));
this.showWallpaper(this.currentIndex, true);
},

showFallbackIfNeeded: function() {
if (this.activeWallpaper || !this.fallbackWallpapers.length) {
return;
}

this.wallpapers = [...this.fallbackWallpapers];
this.currentIndex = 0;
this.showWallpaper(this.currentIndex, true);
},

showWallpaper: function(index, forceThemeRefresh) {
if (!this.wallpapers.length) {
return;
}

this.currentIndex = (index + this.wallpapers.length) % this.wallpapers.length;
this.activeWallpaper = this.wallpapers[this.currentIndex];
this.updateDom(this.config.animationSpeed);

if (forceThemeRefresh || this.activeWallpaper) {
this.applyThemeFromWallpaper(this.activeWallpaper);
}
},

showRelativeWallpaper: function(step) {
if (!this.wallpapers.length) {
return;
}
this.showWallpaper(this.currentIndex + step, false);
},

attachGlobalSwipe: function() {
document.addEventListener("pointerdown", this.boundPointerDown, { passive: true });
document.addEventListener("pointerup", this.boundPointerUp, { passive: true });
},

handlePointerDown: function(event) {
if (this.shouldIgnoreSwipe(event.target)) {
this.pointerStart = null;
return;
}

this.pointerStart = {
x: event.clientX,
y: event.clientY
};
},

handlePointerUp: function(event) {
if (!this.pointerStart || this.shouldIgnoreSwipe(event.target)) {
this.pointerStart = null;
return;
}

const deltaX = event.clientX - this.pointerStart.x;
const deltaY = event.clientY - this.pointerStart.y;
this.pointerStart = null;

if (Math.abs(deltaX) < this.config.swipeThreshold || Math.abs(deltaX) <= Math.abs(deltaY)) {
return;
}

this.showRelativeWallpaper(deltaX < 0 ? 1 : -1);
},

shouldIgnoreSwipe: function(target) {
return Boolean(target.closest(".news-scroller, .language-switch, .quote-card, .customclock-grid, button, .news-list"));
},

applyThemeFromWallpaper: function(imageUrl) {
const image = new Image();
image.onload = () => {
const sampleSize = this.config.themeSampleSize;
const canvas = document.createElement("canvas");
canvas.width = sampleSize;
canvas.height = sampleSize;

const context = canvas.getContext("2d", { willReadFrequently: true });
context.drawImage(image, 0, 0, sampleSize, sampleSize);

const pixels = context.getImageData(0, 0, sampleSize, sampleSize).data;
let red = 0;
let green = 0;
let blue = 0;
let count = 0;

// 璁＄畻缂╃暐閲囨牱鍥剧殑骞冲潎 RGB锛岀敤浜庡姩鎬佸垏鎹㈡祬鑹?娣辫壊涓婚銆?for (let index = 0; index < pixels.length; index += 4) {
red += pixels[index];
green += pixels[index + 1];
blue += pixels[index + 2];
count += 1;
}

red = Math.round(red / count);
green = Math.round(green / count);
blue = Math.round(blue / count);
const luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255;
const isLightTheme = luminance > 0.62;
const root = document.documentElement;
const body = document.body;
const accent = isLightTheme
? `rgba(${Math.max(35, red - 40)}, ${Math.max(80, green - 25)}, ${Math.max(120, blue - 10)}, 0.92)`
: `rgba(${Math.min(220, red + 68)}, ${Math.min(232, green + 66)}, ${Math.min(255, blue + 90)}, 0.9)`;

body.classList.toggle("theme-light", isLightTheme);
body.classList.toggle("theme-dark", !isLightTheme);
root.style.setProperty("--mirror-accent", accent);
root.style.setProperty("--mirror-accent-soft", accent.replace(/0\.[0-9]+\)/, "0.18)"));
root.style.setProperty("--mirror-overlay-strength", this.config.overlayOpacity);
};

image.src = imageUrl;
},

stop: function() {
clearInterval(this.interval);
clearTimeout(this.retryTimer);
document.removeEventListener("pointerdown", this.boundPointerDown);
document.removeEventListener("pointerup", this.boundPointerUp);
}
});

