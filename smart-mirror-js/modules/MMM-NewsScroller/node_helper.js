const NodeHelper = require("node_helper");
const axios = require("axios");
const crypto = require("crypto"); // 百度翻译API签名需要

module.exports = NodeHelper.create({
  start: function() {
    console.log("MMM-NewsScroller node_helper started");
  },

  // 初始化
  socketNotificationReceived: function(notification, payload) {
    if (notification === "INIT") {
      this.config = payload.config;
    }

    // 拉取原始新闻
    if (notification === "FETCH_RAW_NEWS") {
      this.fetchRawNews(payload);
    }

    // 翻译新闻
    if (notification === "TRANSLATE_NEWS") {
      this.translateNews(payload);
    }
  },

  // 拉取原始新闻
  async fetchRawNews(params) {
    try {
      const response = await axios.get(params.url, {
        params: {
          key: params.key,
          type: params.type
        }
      });
      this.sendSocketNotification("RAW_NEWS_RESULT", response.data);
    } catch (error) {
      this.sendSocketNotification("ERROR", "拉取新闻失败: " + error.message);
    }
  },

  // 百度翻译API：翻译新闻内容
  async translateNews(params) {
    const { rawNews, targetLang, appId, secretKey } = params;
    const translatedNews = [];

    // 遍历原始新闻，逐条翻译标题（可扩展翻译分类）
    for (let news of rawNews) {
      try {
        // 百度翻译API参数
        const q = news.title; // 要翻译的内容（新闻标题）
        const salt = Math.random().toString(36).substr(2);
        const sign = crypto.createHash("md5").update(appId + q + salt + secretKey).digest("hex");

        // 调用百度翻译API
        const translateRes = await axios.get("https://fanyi-api.baidu.com/api/trans/vip/translate", {
          params: {
            q,
            from: "auto", // 自动识别原语言
            to: targetLang, // 目标语言（zh/en）
            appid: appId,
            salt,
            sign
          }
        });

        // 保存翻译结果
        translatedNews.push({
          ...news, // 保留原始字段
          translatedTitle: translateRes.data.trans_result[0].dst, // 翻译后的标题
          translatedCategory: targetLang === "en" ? this.translateCategory(news.category) : news.category // 可选：翻译分类
        });
      } catch (error) {
        // 翻译失败时保留原始内容
        translatedNews.push({ ...news });
        console.error("翻译单条新闻失败:", error.message);
      }
    }

    // 发送翻译结果给前端
    this.sendSocketNotification("TRANSLATED_NEWS_RESULT", translatedNews);
  },

  // 手动映射新闻分类（百度翻译可能不够准确）
  translateCategory(category) {
    const map = {
      "国际": "International",
      "国内": "Domestic",
      "娱乐": "Entertainment",
      "体育": "Sports",
      "科技": "Technology"
    };
    return map[category] || category;
  }
});