/**
 * @author Marrion Joseph NTADI
 * @github https://github.com/HeadStone7
 */


Module.register("MMM-BackgroundImage", {
	defaults: {
		height: "100vh",   // 
		width: "100vw",    // 
		animationSpeed: "0",  // 动画速度
		updateInterval: 60 * 60 * 1000,  // 更新间隔，默认每小时更新一次
	},

	start: function() {
        this.wallpaperUrl = null;
        this.specialDate = null;
        
        // 初始化时获取背景图
        this.getWallpaper();
        
        // 设置定时器定期更新
        this.interval = setInterval(() => {
            this.getWallpaper();
        }, this.config.updateInterval);
    },

	getWallpaper: function() {
        const dateInfo = this.getCurrentDateInfo();
        this.sendSocketNotification("GET_WALLPAPER", {
            dateString: dateInfo.dateString,
            modulePath: this.data.path // 传递模块路径给后端
        });
    },

	// 接收node_helper返回的结果
    socketNotificationReceived: function(notification, payload) {
        if (notification === "WALLPAPER_URL") {
            this.wallpaperUrl = payload.url;
            this.updateDom(this.config.animationSpeed);
        }
    },
	getStyles: function() {
		return ["MMM-BackgroundImage.css"];
	},

	getDom: function() {
        const wrapper = document.createElement("div");
        
        if (this.wallpaperUrl) {
            const image = document.createElement("img");
            image.className = "photo";
            image.src = this.wallpaperUrl;
            image.alt = "Background image";
            wrapper.appendChild(image);
        } else {
            // 加载中或出错时显示的内容
            wrapper.innerHTML = "Loading background...";
        }
        
        return wrapper;
    },

	getCurrentDateInfo: function() {
        const now = new Date();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return {
            dateString: `${month}-${day}`
        };
    },

    // 清理定时器
    stop: function() {
        clearInterval(this.interval);
    }
})