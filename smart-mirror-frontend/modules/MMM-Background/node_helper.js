const NodeHelper = require("node_helper");
const fs = require("fs").promises;
const fsSync = require("fs");
const path = require("path");

module.exports = NodeHelper.create({
    festivals: [
        { name: "chongyangjie", date: "09-09", type: "festival" },
        { name: "chunjie", date: "01-01", type: "festival" },
        { name: "duanwujie", date: "05-05", type: "festival" },
        { name: "laba", date: "12-08", type: "festival" },
        { name: "longtaitou", date: "02-08", type: "festival" },
        { name: "qingmingjie", date: "04-05", type: "festival" },
        { name: "qixijie", date: "07-07", type: "festival" },
        { name: "xiaonian", date: "12-23", type: "festival" },
        { name: "yuanxiaojie", date: "01-15", type: "festival" },
        { name: "zhongqiujie", date: "08-15", type: "festival" },
        { name: "zhongyuanjie", date: "06-06", type: "festival" }
    ],

    solar_terms: [
        { name: "01lichun", date: "02-04", type: "solar_term" },
        { name: "02yushui", date: "02-19", type: "solar_term" },
        { name: "03jingzhe", date: "03-05", type: "solar_term" },
        { name: "04chunfen", date: "03-20", type: "solar_term" },
        { name: "05qingming", date: "04-04", type: "solar_term" },
        { name: "06guyu", date: "04-20", type: "solar_term" },
        { name: "07lixia", date: "05-05", type: "solar_term" },
        { name: "08xiaoman", date: "05-21", type: "solar_term" },
        { name: "09mangzhong", date: "06-05", type: "solar_term" },
        { name: "10xiazhi", date: "06-21", type: "solar_term" },
        { name: "11xiaoshu", date: "07-07", type: "solar_term" },
        { name: "12dashu", date: "07-22", type: "solar_term" },
        { name: "13liqiu", date: "08-07", type: "solar_term" },
        { name: "14chushu", date: "08-23", type: "solar_term" },
        { name: "15bailu", date: "09-07", type: "solar_term" },
        { name: "16qiufen", date: "09-23", type: "solar_term" },
        { name: "17hanlu", date: "10-08", type: "solar_term" },
        { name: "18shuangjiang", date: "10-23", type: "solar_term" },
        { name: "19lidong", date: "11-07", type: "solar_term" },
        { name: "20xiaoxue", date: "11-22", type: "solar_term" },
        { name: "21daxue", date: "12-07", type: "solar_term" },
        { name: "22dongzhi", date: "12-22", type: "solar_term" },
        { name: "23xiaohan", date: "01-05", type: "solar_term" },
        { name: "24dahan", date: "01-20", type: "solar_term" }
    ],

    socketNotificationReceived: async function(notification, payload) {
        if (notification !== "GET_WALLPAPER_COLLECTION") {
            return;
        }

        // payload.dateString 鐢卞鎴风鍙戞潵锛?MM-DD" 鏍煎紡锛夛紝鐢ㄤ簬鍒ゆ柇鑺傛皵/鑺傛棩
        await this.handleWallpaperRequest(payload.dateString || "");
    },

    async handleWallpaperRequest(dateString) {
        try {
            // 浣跨敤 __dirname 鑰岄潪瀹㈡埛绔紶鏉ョ殑鐩稿 URL 璺緞锛岄伩鍏嶆湇鍔＄鏂囦欢绯荤粺璺緞瑙ｆ瀽閿欒
            const folderPath = await this.resolveWallpaperFolder(dateString);
            const imageFiles = await this.getImageFiles(folderPath);
            const images = this.shuffle(imageFiles).map((filePath) => {
                const relativePath = this.getRelativePath(filePath, __dirname).replace(/\\/g, "/");
                return `modules/MMM-Background/${relativePath}`;
            });

            this.sendSocketNotification("WALLPAPER_COLLECTION", {
                images,
                initialIndex: images.length ? Math.floor(Math.random() * images.length) : 0
            });
        } catch (error) {
            console.error("MMM-Background: failed to load wallpapers", error);
            this.sendSocketNotification("WALLPAPER_COLLECTION", {
                images: [],
                initialIndex: 0
            });
        }
    },

    async resolveWallpaperFolder(dateString) {
        // 姝ゅ宸查噸鏋勶細鍏堟煡鑺傛皵鍐嶆煡鑺傛棩锛屼繚璇佸悓鏃ュ啿绐佹椂鎸夆€滆妭姘?> 鑺傛棩鈥濇墽琛屻€?        const solarTerm = this.solar_terms.find((item) => item.date === dateString);
        if (solarTerm) {
            const solarTermFolder = path.join(__dirname, "images", "solar_term", solarTerm.name);
            if (fsSync.existsSync(solarTermFolder)) {
                return solarTermFolder;
            }
        }

        const festival = this.festivals.find((item) => item.date === dateString);
        if (festival) {
            const festivalFolder = path.join(__dirname, "images", "festival", festival.name);
            if (fsSync.existsSync(festivalFolder)) {
                return festivalFolder;
            }
        }

        // 鍏煎鍘嗗彶鐩綍鍚嶏紝閬垮厤鍥?cultures/culture 宸紓瀵艰嚧鏃犲绾搞€?        const culturesFolder = path.join(__dirname, "images", "cultures");
        if (fsSync.existsSync(culturesFolder)) {
            return culturesFolder;
        }

        return path.join(__dirname, "images", "culture");
    },

    async getImageFiles(folderPath) {
        if (!fsSync.existsSync(folderPath)) {
            return [];
        }

        const files = await fs.readdir(folderPath);
        return files
            .filter((file) => [".jpg", ".jpeg", ".png", ".gif", ".webp"].includes(path.extname(file).toLowerCase()))
            .map((file) => path.join(folderPath, file));
    },

    getRelativePath(filePath, modulePath) {
        return path.relative(modulePath, filePath);
    },

    shuffle(list) {
        const copy = [...list];
        for (let index = copy.length - 1; index > 0; index -= 1) {
            const randomIndex = Math.floor(Math.random() * (index + 1));
            [copy[index], copy[randomIndex]] = [copy[randomIndex], copy[index]];
        }
        return copy;
    }
});

