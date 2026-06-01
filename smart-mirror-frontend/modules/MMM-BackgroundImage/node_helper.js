const NodeHelper = require("node_helper");
const fs = require('fs').promises; // 使用异步文件操作
const fsSync = require('fs'); // 用于检查文件是否存在
const path = require('path');
const { log } = require("console");

module.exports = NodeHelper.create({
    // 中国节日数据集合
    festivals: [
        { name: 'chongyang', date: '09-09', type: 'festival', description: '重阳节，又称老人节，象征着敬老爱老。' },
        { name: 'chunjie', date: '01-01', type: 'festival', description: '春节是中国最重要的传统节日，象征新的开始与团圆。' },
        { name: 'duanwujie', date: '05-05', type: 'festival', description: '端午节，为纪念屈原而设，有吃粽子、赛龙舟等习俗。' },
        { name: 'laba', date: '12-08', type: 'festival', description: '腊八节，传统上是祭祀祖先的日子，也是腊月的开始。' },
        { name: 'longtaitou', date: '02-08', type: 'festival', description: '龙抬头，农历二月初二，象征着春天的到来和农耕的开始。' },
        { name: 'qingmingjie', date: '04-05', type: 'festival', description: '清明节是中国传统节日，也是最重要的祭祀节日之一。' },
        { name: 'qixijie', date: '07-07', type: 'festival', description: '七夕节，又称中国情人节，是牛郎织女相会的日子。' },
        { name: 'xiaonian', date: '12-23', type: 'festival', description: '小年，传统上是祭灶的日子，标志着春节准备的开始。' },
        { name: 'yuanxiaojie', date: '01-15', type: 'festival', description: '元宵节，又称上元节，是春节后的第一个重要节日。' },
        { name: 'zhongqiujie', date: '08-15', type: 'festival', description: '中秋节，象征团圆，有赏月、吃月饼的习俗。' },
        { name: 'zhongyuejie', date: '06-06', type: 'festival', description: '中元节，又称鬼节，是祭祀祖先和亡灵的日子。' },
    ],

    // 二十四节气数据集合
    solar_terms: [
        { name: '01lichun', date: '02-04', type: 'solar_term', description: '立春，二十四节气之首，标志着春季的开始。' },
        { name: '02yushui', date: '02-19', type: 'solar_term', description: '雨水，表示降雨开始，雨量渐增。' },
        { name: '03jingzhe', date: '03-05', type: 'solar_term', description: '惊蛰，春雷始鸣，惊醒蛰伏于地下冬眠的昆虫。' },
        { name: '04chunfen', date: '03-20', type: 'solar_term', description: '春分，昼夜平分，春季九十日平分。' },
        { name: '05qingming', date: '04-04', type: 'solar_term', description: '清明，天气晴朗，草木繁茂。' },
        { name: '06guyu', date: '04-20', type: 'solar_term', description: '谷雨，雨生百谷，雨量充足而及时。' },
        { name: '07lixia', date: '05-05', type: 'solar_term', description: '立夏，夏季的开始。' },
        { name: '08xiaoman', date: '05-21', type: 'solar_term', description: '小满，麦类等夏熟作物籽粒开始饱满。' },
        { name: '09mangzhong', date: '06-05', type: 'solar_term', description: '芒种，麦类等有芒作物成熟。' },
        { name: '10xiazhi', date: '06-21', type: 'solar_term', description: '夏至，炎热的夏天来临。' },
        { name: '11xiaoshu', date: '07-07', type: 'solar_term', description: '小暑，暑热开始，但还未达到最热。' },
        { name: '12dashu', date: '07-22', type: 'solar_term', description: '大暑，一年中最热的时候。' },
        { name: '13liqiu', date: '08-07', type: 'solar_term', description: '立秋，秋季的开始。' },
        { name: '14chushu', date: '08-23', type: 'solar_term', description: '处暑，"处"为结束的意思，暑气即将结束。' },
        { name: '15baixu', date: '09-07', type: 'solar_term', description: '白露，天气转凉，露凝而白。' },
        { name: '16qiufen', date: '09-23', type: 'solar_term', description: '秋分，昼夜平分。' },
        { name: '17hanshuang', date: '10-08', type: 'solar_term', description: '寒露，露水已寒，将要结冰。' },
        { name: '18shuangjiang', date: '10-23', type: 'solar_term', description: '霜降，天气渐冷，开始有霜。' },
        { name: '19lidong', date: '11-07', type: 'solar_term', description: '立冬，冬季的开始。' },
        { name: '20xiaoxue', date: '11-22', type: 'solar_term', description: '小雪，开始下雪。' },
        { name: '21daxue', date: '12-07', type: 'solar_term', description: '大雪，降雪量增多，地面可能积雪。' },
        { name: '22dongzhi', date: '12-22', type: 'solar_term', description: '冬至，寒冷的冬天来临，北半球白昼最短。' },
        { name: '23xiaohan', date: '01-05', type: 'solar_term', description: '小寒，气候开始寒冷。' },
        { name: '24dahan', date: '01-20', type: 'solar_term', description: '大寒，一年中最冷的时候。' }
    ],

    start: function() {
        console.log("MMM-BackgroundImage helper started...");
    },

    // 处理前端发送的通知
    socketNotificationReceived: function(notification, payload) {
        if (notification === "GET_WALLPAPER") {
            console.log("MMM-BackgroundImage helper: received GET_WALLPAPER, dateString:", payload.dateString);
            console.log("MMM-BackgroundImage helper: modulePath:", payload.modulePath);
            this.handleWallpaperRequest(payload);
        }
    },

    // 处理壁纸请求
    async handleWallpaperRequest(payload) {
        try {
            const allSpecialDates = [...this.festivals, ...this.solar_terms];
            const specialDate = allSpecialDates.find(item => item.date === payload.dateString);

            let wallpaperUrl = null;
            if (specialDate) {
                const specialPath = path.join(payload.modulePath, 'images', specialDate.type, specialDate.name);
                console.log("MMM-BackgroundImage helper: special date found:", specialDate.name, "path:", specialPath);
                wallpaperUrl = await this.getRandomFileFromFolder(specialPath);
            }

            // 如果特殊日期没有图片，使用默认图片
            if (!wallpaperUrl) {
                const fallbackPath = path.join(payload.modulePath, 'images', 'culture');
                console.log("MMM-BackgroundImage helper: using fallback path:", fallbackPath);
                wallpaperUrl = await this.getRandomFileFromFolder(fallbackPath);
            }

            const finalUrl = wallpaperUrl ? `modules/MMM-BackgroundImage/${this.getRelativePath(wallpaperUrl, payload.modulePath)}` : null;
            console.log("MMM-BackgroundImage helper: sending WALLPAPER_URL:", finalUrl);

            // 发送结果给前端
            this.sendSocketNotification("WALLPAPER_URL", {
                url: finalUrl
            });

        } catch (error) {
            console.error("Error handling wallpaper request:", error);
            this.sendSocketNotification("WALLPAPER_URL", { url: null });
        }
    },

    // 获取文件夹中随机一个文件
    async getRandomFileFromFolder(folderPath) {
        try {
            // 检查文件夹是否存在
            if (!fsSync.existsSync(folderPath)) {
                console.log(`Folder not found: ${folderPath}`);
                return null;
            }

            // 异步读取文件夹
            const files = await fs.readdir(folderPath);

            // 过滤出图片文件
            const imageFiles = files.filter(file => {
                const ext = path.extname(file).toLowerCase();
                return ['.jpg', '.jpeg', '.png', '.gif', '.webp'].includes(ext);
            });

            if (imageFiles.length === 0) {
                console.log(`No image files found in: ${folderPath}`);
                return null;
            }

            // 随机选择一个图片
            const randomIndex = Math.floor(Math.random() * imageFiles.length);
            const result = path.join(folderPath, imageFiles[randomIndex]);
            console.log(`Selected image: ${result}`);
            return result;

        } catch (error) {
            console.error(`Error reading folder ${folderPath}:`, error);
            return null;
        }
    },

    // 生成相对于模块的路径（修复的核心部分）
    getRelativePath(filePath, modulePath) {
        return path.relative(modulePath, filePath);
    }
});