Module.register('MMM-CalligraphyButton', {
    // 模块默认配置（可自定义按钮文字、目标页面路径）
    defaults: {
        buttonText: "生成书法作品",
        targetPage: "calligraphy.html", // 二级界面的HTML文件名，需与模块同目录
        // 多语言文字映射（中文/英文）
        langMap: {
            "Zh-cn": "生成书法作品",
            "En-us": "Create calligraphy works"
        }
    },

    // 保存当前语言和动画状态
    state: {
        currentLanguage: null
    },

    // 模块启动初始化语言
    start: function() {
        // 从系统获取当前语言
        this.state.currentLanguage = localStorage.getItem("mm_language") || config.language;
    },

    // 生成页面DOM（渲染按钮）
    getDom: function() {
        const wrapper = document.createElement("div");
        const button = document.createElement("button");
        
        // 根据当前语言动态设置按钮文字
        const btnText = this.config.langMap[this.state.currentLanguage] || this.config.buttonText;
        button.innerHTML = btnText; // 按钮显示的文字
        
        button.className = "calligraphy-btn";       // 自定义CSS类（用于美化）
        button.addEventListener("click", () => {
            // 点击按钮 → 跳转到二级界面
            window.location.href = this.file(this.config.targetPage);
        });
        
        wrapper.appendChild(button);

        // 首次加载触发渐入动画
        setTimeout(() => {
            button.classList.add("btn-fade-active");
        }, 100);

        return wrapper;
    },

    // 引入自定义样式（美化按钮）
    getStyles: function() {
        return ["MMM-CalligraphyButton.css"];
    },

    // 监听器(fjyi)
    notificationReceived: function(notification, payload) {
        if (notification === "LANGUAGE_CHANGED") {
            const oldLang = this.state.currentLanguage;
            this.state.currentLanguage = payload; // 更新语言
            
            // 找到按钮元素，先移除动画类（淡出），再更新文字并添加动画类（淡入）
            const button = document.querySelector(".calligraphy-btn");
            if (button && oldLang !== payload) {
                button.classList.remove("btn-fade-active");
                // 延迟匹配CSS动画时长，确保淡出后更新文字
                setTimeout(() => {
                    button.innerHTML = this.config.langMap[payload] || this.config.buttonText;
                    button.classList.add("btn-fade-active");
                }, 300);
            }
        }
    }
});