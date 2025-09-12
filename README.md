# Smart Mirror 智能镜子项目

## 项目简介
国创项目，基于树莓派开发，基于Python3.（!高于这个版本建议降低到此版本!）开发，基于阿里/百度等AI开放平台开发，基于DeepSeek大模型开发。
本项目是一个基于Python的智能镜子系统，结合了语音识别、面部识别和AI对话技术，提供自然的人机交互体验。

## 核心功能
1. **唤醒词检测**：支持自定义关键词唤醒（"你好", "树莓派", "小", "小朋友", "朋友"）
2. **面部识别**：通过摄像头进行用户身份验证
3. **语音交互**：支持语音控制以下功能：
   - 实时天气查询与播报
   - 时间查询
   - 空调控制
   - AI智能对话（基于DeepSeek等大模型）
4. **多平台显示**：支持PyQt5/Kivy/控制台三种显示模式

## 技术架构
```
+-------------------+
|     用户界面       |
| (PyQt5/Kivy/CLI) |
+-------------------+
        |
+-----------------------------+
|      语音识别/合成模块          |
|   (百度/paraformer API集成)   |
+-----------------------------+
        |
+-------------------+
|     智能决策引擎    |
| (DeepSeek/qwen大模型)  |
+-------------------+
        |
+-------------------+
| 设备控制接口模块  |
| (MCP控制/传感器)   |
+-------------------+
```

## 系统要求
- Python 3.8+
- 树莓派或其他嵌入式设备
- 麦克风和扬声器
- 摄像头
- 百度AI开放平台API密钥
- DeepSeek API密钥
- 其他要求

## 安装指南
请参考[INSTALL.md](smart-mirror-main/doc/INSTALL.md)

## 开发规范
请参考[CODING_STYLE.md](smart-mirror-main/doc/CODING_STYLE.md)

## 贡献指南
请参考[CONTRIBUTING.md](smart-mirror-main/doc/CONTRIBUTING.md)

## 本仓库使用了以下仓库的代码
[https://github.com/HeadStone7/smart-mirror](https://github.com/HeadStone7/smart-mirror)

[https://github.com/SunnyBoy-y/smart_mirror_gc_main](https://github.com/SunnyBoy-y/smart_mirror_gc_main)

# 这是一个国创项目，基于学长学姐们的代码基础修改，感谢@HeadStone7；@niezhili的贡献！