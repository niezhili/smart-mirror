# Smart Mirror 智能镜子 — 产品需求文档（PRD）

> **版本**：v1.0  
> **日期**：2026-04-04  
> **项目性质**：国家大学生创新创业训练计划项目（国创项目）

---

## 目录

1. [项目背景与定位](#1-项目背景与定位)
2. [产品目标](#2-产品目标)
3. [系统整体架构](#3-系统整体架构)
4. [硬件平台](#4-硬件平台)
5. [功能模块详述](#5-功能模块详述)
  - 5.1 显示前端（smart-mirror-frontend）
  - 5.2 后端服务（smart-mirror-backend）
   - 5.3 唤醒词与语音活动检测（VAD）
   - 5.4 语音识别（ASR）
   - 5.5 大语言模型对话（LLM）
   - 5.6 语音合成（TTS）
   - 5.7 人脸识别
   - 5.8 人体检测
   - 5.9 天气服务
   - 5.10 家居控制（空调控制）
   - 5.11 IoT 远程通信（Blinker）
   - 5.12 视线估计（GazeEstimator）
6. [非功能性需求](#6-非功能性需求)
7. [外部依赖与第三方 API](#7-外部依赖与第三方-api)
8. [开发规范](#8-开发规范)
9. [环境部署](#9-环境部署)
10. [已知限制与后续规划](#10-已知限制与后续规划)

---

## 1. 项目背景与定位

**Smart Mirror** 是一款部署在树莓派（Raspberry Pi）上的智能镜子系统，旨在将普通镜子升级为具有自然人机交互能力的"智能终端"。系统融合了：

- 计算机视觉（人脸识别、人体检测、视线估计）
- 语音交互（唤醒词检测 → 语音识别 → LLM 推理 → 语音合成）
- 信息展示（时钟、日历、实时天气、新闻滚动）
- 智能家居控制（空调红外控制、IoT 远程通信）

项目基于学长学姐的代码基础（[@HeadStone7](https://github.com/HeadStone7/smart-mirror)、[@niezhili](https://github.com/SunnyBoy-y/smart_mirror_gc_main)）进行扩展开发。

### 使用场景

用户站在镜子前时，系统自动感知人体靠近，唤醒后进入语音交互模式。用户可以通过自然语言查天气、聊天、控制家电，同时在镜面上看到时间、日历、天气、新闻等实时信息。

---

## 2. 产品目标

| 目标 | 描述 |
|------|------|
| **自然交互** | 用户无需触屏，通过语音即可获取信息和控制设备 |
| **身份识别** | 通过人脸识别区分不同用户，提供个性化问候 |
| **信息中枢** | 在镜面上展示时间、日历、天气、新闻等生活信息 |
| **智能家居** | 语音控制空调等家电设备 |
| **多语言支持** | 支持中文、英语、日语三语交互 |
| **低功耗运行** | 通过人体检测按需激活，避免持续运行耗能 |

---

## 3. 系统整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        硬件层（树莓派）                         │
│  摄像头 | 麦克风 | 扬声器 | PIR传感器 | DHT11 | 红外发射模块     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                      后端服务（Python 3.8）                    │
│                   smart-mirror-backend/                      │
│                                                              │
│  ┌─────────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────────┐  │
│  │  VAD    │  │ ASR  │  │ LLM  │  │ TTS  │  │ 人脸识别  │  │
│  │(Silero) │  │(Para │  │(Qwen/│  │(火山/ │  │(dlib/    │  │
│  │         │  │former│  │Deep  │  │百度)  │  │OpenCV)   │  │
│  └────┬────┘  └──┬───┘  └──┬───┘  └──┬───┘  └──────────┘  │
│       └──────────┴──────────┴──────────┘                    │
│                    Flask Web Server (:8080)                  │
│       ┌────────────────┬────────────────┐                   │
│       │  home_control  │  人体检测(GPIO)  │                  │
│       │ (AC/涂鸦API)   │  PIR 红外传感   │                   │
│       └────────────────┴────────────────┘                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP (localhost:8080)
┌──────────────────────▼──────────────────────────────────────┐
│                    前端显示（Node.js + Electron）              │
│                  smart-mirror-frontend/                      │
│                   基于 MagicMirror² 框架                      │
│                                                              │
│  时钟 | 日历 | 天气 | 新闻滚动 | DHT11 | 背景图 | 语录        │
└─────────────────────────────────────────────────────────────┘
                       │ 局域网
┌──────────────────────▼───────────┐
│      IoT 远程控制（Blinker APP）   │
│         LED / 传感器数据上报        │
└───────────────────────────────────┘
```

### 子系统划分

| 目录 | 技术栈 | 职责 |
|------|--------|------|
| `smart-mirror-backend/` | Python 3.8, Flask | 后端核心逻辑（语音、AI、人脸、家控） |
| `smart-mirror-frontend/` | Node.js, MagicMirror², Electron | 前端镜面信息展示 |
| `smart-mirror-backend/features/iot/blinker/` | Python, MQTT | IoT 远程控制与数据上报 |
| `smart-mirror-backend/features/gaze_estimation/` | Python（配置驱动） | 视线估计模块 |

---

## 4. 硬件平台

### 必需硬件

| 硬件 | 型号/规格 | 用途 |
|------|-----------|------|
| 主控板 | Raspberry Pi 4 / 3B+ | 系统运行 |
| 摄像头 | Pi Camera / USB 摄像头 | 人脸识别、视线估计 |
| 麦克风 | USB 麦克风阵列 | 语音采集 |
| 扬声器 | 3.5mm / USB 音频 | TTS 语音播报 |
| 显示屏 | HDMI 镜面显示器 | 信息展示 |
| PIR 传感器 | HC-SR501（GPIO BCM 17） | 人体检测 |
| DHT11 传感器 | GPIO BCM 4 | 室内温湿度采集 |
| 红外发射模块 | 连接 GPIO BCM 18 | 空调红外控制 |

### GPIO 引脚映射（BCM 模式）

| GPIO Pin | 功能 |
|----------|------|
| BCM 17 | PIR 人体探测传感器输入 |
| BCM 18 | 红外发射模块输出（空调控制） |
| BCM 4 | DHT11 数据引脚 |

---

## 5. 功能模块详述

### 5.1 显示前端（smart-mirror-frontend）

基于开源 [MagicMirror²](https://magicmirror.builders/) 框架，通过 Electron 封装为桌面应用，监听 `localhost:8080`，以全屏方式渲染镜面 UI。

#### 内置模块

| 模块名 | 来源 | 功能 |
|--------|------|------|
| `clock` | 原生 | 数字时钟 |
| `MMM-Clock` | 自研 | 支持中文格式的自定义时钟 |
| `MMM-Clockinese` | 自研 | 中文时钟显示样式 |
| `calendar` | 原生 | 日历事件 |
| `MMM-Calendar` | 自研 | 月历视图 |
| `MMM-Weather` | 自研 | 接入和风天气 API 的天气展示 |
| `MMM-DHT11` | 自研 | 实时室内温湿度展示（DHT11 传感器，500ms 刷新） |
| `MMM-News` | 自研 | 新闻滚动播报（接入聚合数据 API） |
| `MMM-Background` | 自研 | 镜面背景图管理 |
| `MMM-Quote` | 自研 | 每日语录/名言 |
| `MMM-Language` | 自研 | 界面语言切换 |
| `updatenotification` | 原生 | 更新提醒 |

#### 前端配置（`smart-mirror-frontend/config/config.js`）

```js
let config = {
  address: "localhost",
  port: 8080,
  language: "zh-cn",
  timeFormat: 24,
  units: "metric",
  // ... 各模块配置
};
```

---

### 5.2 后端服务（smart-mirror-backend）

入口文件：`main.py`。使用 Flask 在后台启动 Web 服务器，同时管理语音交互主循环。

#### 主流程

```
系统启动
   │
   ├─ 预加载人脸数据（已知人脸文件夹）
   ├─ 启动人体检测线程（PIR 传感器）
   ├─ 获取地理位置（IP 定位）
   ├─ 启动 Flask 服务器（:8080）
   │
   └─ 主循环
         │
         ├─ 监听唤醒词
         │      │
         │      └─ 检测到唤醒词
         │               │
         │               ├─ 人脸识别验证
         │               │      │成功
         │               │      └─ 进入语音交互模式
         │               │               │
         │               │               ├─ VAD 录制用户语音
         │               │               ├─ ASR 语音转文字
         │               │               ├─ 意图判断（天气/时间/空调/AI对话）
         │               │               ├─ 执行对应功能
         │               │               └─ TTS 语音播报结果
         │               │
         │               └─ 人脸识别失败 → 提示验证失败
         │
         └─ 超时（300s）→ 退出交互模式
```

---

### 5.3 唤醒词与语音活动检测（VAD）

#### 唤醒词

在 `config/config.yaml` 中配置，默认支持：

```yaml
wakeup_words: ["你好", "树莓派", "小", "小朋友", "朋友", "小镜子"]
```

#### VAD 模块（`features/vad/vad.py`）

- 使用 **Silero VAD** 模型（本地加载，无网络依赖）进行语音活动检测
- 关键参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `confidence` | 0.3 | 人声置信度阈值 |
| `silence` | 1s | 静音持续时长判定说话结束 |
| `timeout` | 600s | 录制总超时 |
| `sample_rate` | 16000 Hz | 音频采样率 |
| `chunk` | 512 帧 | 每次读取帧数 |

- 模型文件路径：`features/common/model/silero_vad/`

---

### 5.4 语音识别（ASR）

模块路径：`features/asr/`

支持两种 ASR 后端，通过 `config.yaml` 的 `choose.asr` 字段切换：

| 后端标识 | 服务商 | 模型 | 支持语言 |
|----------|--------|------|----------|
| `paraformer` | 阿里云 DashScope | `paraformer-realtime-v2` | 中文、英语、日语 |
| `asr_baidu` | 百度 AI 开放平台 | 普通话模型（dev_pid: 1537） | 中文 |

#### Paraformer 调用示例

```python
from features.asr.asr_paraformer import speech_to_text_paraformer

text = speech_to_text_paraformer(
    audio_file_path="recording.wav",
    api_key="sk-xxx",
    model="paraformer-realtime-v2",
    sample_rate=16000,
    language_hints=["zh", "en", "ja"]
)
```

---

### 5.5 大语言模型对话（LLM）

模块路径：`features/llm/`

#### 角色人设

AI 助手名为 **"小镜"** / **"小朋友"**，人设定义于 `config.yaml`：

> 你是一款知书达理的多语言汉学互联镜，能够说中英日三国语言，集成摄像头、麦克风等外设，擅长引经据典。说话简洁精准，不失幽默。请多用口语，不用 Markdown 格式。每次回复尽量不超过 100 字。

#### 支持后端

| 后端标识 | 服务商 | 模型 |
|----------|--------|------|
| `qwen` | 阿里云 DashScope | `qwen-turbo` |
| `deepseek` | DeepSeek | DeepSeek Chat API |

#### 上下文管理（`features/llm/context_manager.py`）

- 每个用户（`user_id`）维护独立的对话上下文
- 系统 Prompt 从 `config.yaml` 的 `context_manager.role` 字段读取
- 对话轮次持久存储在上下文对象中，支持多轮连续对话

#### 语言切换逻辑

1. 若用户明确要求某种语言 → 始终使用该语言（最高优先级）
2. 若未指定 → 跟随用户提问语言作答（次高优先级）

---

### 5.6 语音合成（TTS）

模块路径：`features/tts/`

支持三种 TTS 后端，通过 `config.yaml` 的 `choose.tts` 字段切换：

| 后端标识 | 服务商 | 协议 | 特点 |
|----------|--------|------|------|
| `tts_huoshan` | 字节跳动（火山引擎） | WebSocket | 多情感、多语言、多音色 |
| `tts_huoshan_fast` | 字节跳动（火山引擎）快速版 | WebSocket | 低延迟 |
| `tts_baidu` | 百度 AI 开放平台 | HTTP | 通用中文 TTS |
| `tts_aliyun` | 阿里云 | — | 备选 |

#### 火山引擎 TTS 音色配置

```yaml
tts_huoshan:
  voice_type:
    default: "zh_female_yingyujiaoyu_mars_bigtts"   # 中英文
    ja: "multi_male_jingqiangkanye_moon_bigtts"       # 日文
    en: "multi_male_jingqiangkanye_moon_bigtts"       # 英文
  motion_type: "happy"   # 情感：happy/sad/angry/tender/storytelling...
```

支持的情感类型（中文）：开心、悲伤、生气、惊讶、恐惧、厌恶、激动、冷漠、中性、沮丧、撒娇、害羞、安慰、咆哮、温柔、讲故事、情感电台、磁性等。

---

### 5.7 人脸识别

模块路径：`features/face_recognition/face_recognition_system.py`

#### 技术栈

- `face_recognition`（基于 dlib）：人脸编码提取与比对
- `OpenCV`：摄像头视频流采集与预处理

#### 主要参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `known_faces_dir` | `known_faces/` | 已知人脸图片目录 |
| `recognition_threshold` | 0.6 | 人脸识别相似度阈值（越低越严格） |
| `min_face_size` | 20px | 最小检测人脸尺寸 |
| `face_detect_timeout` | 30s | 单次人脸识别超时 |

#### 流程

1. 启动时从 `known_faces/<人名>/` 目录批量加载已知人脸图片并编码缓存
2. 调用 `start_recognition()` 开启摄像头实时比对
3. 识别成功 → 语音问候（TTS）+ 返回 `True`
4. 超时或不匹配 → 返回 `False`

#### 已知人脸管理

将人脸照片（JPG）放入 `known_faces/<姓名>/` 目录下，系统启动时自动加载，支持多张照片提高识别准确率。

---

### 5.8 人体检测

文件：`features/human_detection.py`

使用 PIR（被动红外）传感器检测人体是否靠近镜子，作为系统主动唤醒的触发器，避免持续监听耗电。

#### 配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `pin` | BCM 17 | PIR 传感器 GPIO 引脚 |
| `timeout` | 15s | 人体离开后的保活时间 |
| `consecutive_detections_required` | 2 | 触发所需连续检测次数（防抖） |
| `trigger_cooldown` | 10s | 触发冷却时间（防重复触发） |

> **注意**：在 Windows 开发环境无法使用 GPIO，需在 `config.yaml` 中将 `human_detection` 设为 `False`。

---

### 5.9 天气服务

模块路径：`features/weather/`

- **API 来源**：[和风天气（QWeather）](https://www.qweather.com/)
- 通过 IP 自动定位（`geocoder` 库）获取当前经纬度，再调用天气 API

#### 返回数据字段

```python
{
    "weather_condition": "晴",       # 天气状况
    "temperature": "25°C",           # 实时温度
    "feels_like": "27°C",            # 体感温度
    "humidity": "60%",               # 湿度
    "wind_direction": "东南风",       # 风向
    "wind_speed": "3 m/s",           # 风速
    "pressure": "1013 hPa",          # 气压
    "visibility": "10 km",           # 能见度
}
```

用户语音询问天气时，系统获取数据后通过 TTS 播报天气概要。

---

### 5.10 家居控制（空调控制）

文件：`home_control/ac_control.py`

提供两种空调控制方式：

#### 方式一：涂鸦 API + 红外发射模块（主要方式）

- 通过 Tuya OpenAPI 获取红外编码
- 控制 BCM 18 GPIO 红外发射模块发出信号
- 需配置 `config.yaml` 中 `iot.tuya_api_id` 和 `iot.tuya_api_secret`

#### 方式二：MQTT 控制（规划中，暂未实现）

#### 空调状态管理

```python
ac_status = {
    'power': False,        # 开关状态
    'temperature': 25,     # 设定温度
    'mode': 'cool',        # 模式：cool/heat/auto/dry/fan
    'fan_speed': 'auto'    # 风速：auto/low/medium/high
}
```

用户通过语音指令（如"开空调"、"温度调到 26 度"）触发对应操作。

---

### 5.11 IoT 远程通信（Blinker）

文件：`smart-mirror-backend/features/iot/blinker/blinker_raspberrypi.py`

通过 [Blinker](https://diandeng.tech/home) 平台实现手机 APP 与树莓派的局域网通信：

- APP 按钮控制 LED 开关（GPIO BCM 18）
- 每 2 秒自动上报传感器数据（温度等）
- 支持通过 systemd 服务（`smart-mirror-backend/features/iot/blinker/blinker.service`）开机自启动

**通信加固**：建议为树莓派设置固定 IP，并定期更新依赖库。

---

### 5.12 视线估计（GazeEstimator）

目录：`smart-mirror-backend/features/gaze_estimation/`，包含 `config.json` 配置文件。

该模块旨在通过摄像头估计用户视线方向，用于判断用户是否在注视镜子，从而触发更精细的交互逻辑（如自动激活显示）。具体算法实现为规划/接入中状态。

---

## 6. 非功能性需求

| 类别 | 要求 |
|------|------|
| **响应延迟** | 语音识别 + LLM 推理 + TTS 合成总延迟 ≤ 5s（网络正常情况） |
| **稳定性** | 主进程异常捕获，模块故障不导致整体崩溃 |
| **并发** | 多线程处理：人体检测、人脸识别、语音交互相互独立 |
| **低功耗** | 无人靠近时 PIR 传感器驱动按需激活，减少 CPU 占用 |
| **安全** | API 密钥不提交到代码仓库（存于 `config.yaml`，`.gitignore` 处理） |
| **可扩展** | 新 ASR/TTS/LLM 后端通过修改配置即可切换，无需改动核心逻辑 |
| **多语言** | 界面、语音交互同时支持中文、英语、日语 |

---

## 7. 外部依赖与第三方 API

### 云服务 API

| 服务 | 提供商 | 用途 | 配置键 |
|------|--------|------|--------|
| Paraformer ASR | 阿里云 DashScope | 多语言语音识别 | `asr.paraformer.api_key` |
| 百度 ASR | 百度 AI 开放平台 | 中文语音识别（备选） | `asr.asr_baidu.*` |
| 火山 TTS | 字节跳动火山引擎 | 情感化语音合成 | `tts.tts_huoshan.*` |
| 百度 TTS | 百度 AI 开放平台 | 中文语音合成（备选） | `tts.tts_baidu.*` |
| Qwen 通义千问 | 阿里云 DashScope | 大语言模型对话 | `llm.qwen.*` |
| DeepSeek | DeepSeek 官方 | 大语言模型对话（备选） | `llm.deepseek.*` |
| 和风天气 | QWeather | 实时天气查询 | `weather.weather_api_key` |
| 聚合数据新闻 | juhe.cn | 新闻内容 | 前端模块配置 |
| 涂鸦 IoT | Tuya Smart | 红外智能控制 | `iot.tuya_api_id` |

### 主要 Python 依赖库

| 库 | 版本 | 用途 |
|----|------|------|
| `flask` | — | 后端 Web 服务器 |
| `pyyaml` | ~=6.0.2 | 配置文件解析 |
| `pyaudio` | — | 音频采集 |
| `face_recognition` | — | 人脸识别（基于 dlib） |
| `opencv-python` | — | 摄像头图像处理 |
| `dashscope` | — | 调用阿里云 ASR / LLM |
| `loguru` | — | 结构化日志 |
| `geocoder` | — | IP 地理位置定位 |
| `websockets` | — | 火山 TTS WebSocket 通信 |
| `RPi.GPIO` | — | 树莓派 GPIO 控制 |
| `torch` | — | Silero VAD 模型推理 |
| `pyttsx3` | ~=2.98 | 系统 TTS（人脸识别模块本地语音） |
| `requests` | — | HTTP 请求 |
| `pywebview` | — | 嵌入式 Web 视图 |

### 前端依赖

基于 MagicMirror² 框架（Node.js），通过 `npm install` 安装，核心依赖在 `smart-mirror-frontend/package.json` 中定义；Electron 用于将前端封装为桌面应用。

---

## 8. 开发规范

详见 [CODING_STYLE.md](smart-mirror-backend/docs/CODING_STYLE.md)，核心约定如下：

### 目录结构规范

```
smart-mirror-backend/
├── config/               # 配置文件
├── docs/                 # 文档
├── features/             # 功能模块
│   ├── asr/              # 语音识别
│   ├── common/           # 公共组件
│   ├── face_recognition/ # 人脸识别
│   ├── gaze_estimation/  # 视线估计
│   ├── human_detection.py # 人体检测
│   ├── iot/              # IoT 模块（Blinker）
│   ├── llm/              # 大语言模型
│   ├── tts/              # 语音合成
│   ├── vad/              # 语音活动检测
│   └── weather/          # 天气服务
├── home_control/         # 家居控制
├── known_faces/          # 已知人脸图片
├── tests/                # 测试文件
└── log/                  # 日志输出
```

### 日志规范

使用 `loguru` 库，每个模块必须绑定标签：

```python
from features.common.log_loader import logger

TAG = __name__
logger.bind(tag=TAG).info("日志内容")
```

日志级别：`DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`

### 配置使用规范

所有配置集中在 `config/config.yaml`，通过统一入口读取：

```python
from features.common.config_loader import config
api_key = config['llm']['qwen']['qwen_api_key']
```

**安全要求**：API 密钥等敏感信息不得提交到代码仓库。

### 模块设计原则

- 每个功能模块独立封装在单独目录中
- 公共组件统一放在 `features/common/`
- ASR/TTS/LLM 支持多后端，通过配置切换，核心逻辑不耦合具体实现

### 命名规范

- Python 后端：文件/模块/函数使用 `snake_case`，类使用 `PascalCase`
- JavaScript 前端：变量/函数使用 `camelCase`，类使用 `PascalCase`
- 跨端目录命名：统一使用 `kebab-case`（如 `smart-mirror-frontend`、`smart-mirror-backend`）

---

## 9. 环境部署

### 后端部署

```bash
# 1. 创建 conda 环境
conda create -n smart_mirror python=3.8
conda activate smart_mirror

# 2. 安装依赖
pip install -r requirements.txt

# 3. 如果 dlib 编译失败，改用预编译版本
conda install -c conda-forge dlib

# 4. 配置 API 密钥
cp config/config.yaml.sample config/config.yaml
# 编辑 config.yaml 填入各 API Key

# 5. 准备已知人脸
mkdir -p known_faces/<用户名>
# 将人脸照片放入对应目录（JPG 格式）

# 6. 启动后端
python main.py
```

### 前端部署

```bash
cd smart-mirror-frontend
npm install
cp config/config.js.sample config/config.js
# 编辑 config.js 配置各模块
npm start
```

### 开发环境注意事项

- Windows 下无法使用 RPi.GPIO，需在 `config.yaml` 中设置 `human_detection: False`
- Silero VAD 模型需提前下载到 `features/common/model/silero_vad/` 目录

---

## 10. 已知限制与后续规划

### 当前限制

| 限制 | 说明 |
|------|------|
| GPIO 依赖 | 人体检测、红外控制仅支持树莓派，Windows/macOS 开发需关闭 |
| MQTT 空调控制 | 代码中已有接口定义，但功能未实现 |
| DeepSeek 后端 | `deepseek_chat()` 函数体为 `pass`，待实现 |
| 视线估计 | `features/gaze_estimation/` 当前以配置驱动为主，算法待完善 |
| 唤醒词精度 | 当前为关键词匹配，存在误唤醒风险 |
| 网络依赖 | ASR/LLM/TTS 均依赖外部云 API，离线场景不可用 |

### 后续规划

1. 完善 DeepSeek LLM 后端接入
2. 实现 MQTT 协议的 WiFi 空调控制
3. 完善视线估计模块，支持"用户注视触发亮屏"
4. 接入本地小模型（如 Whisper）实现离线语音识别
5. 增加用户配置界面（Web 管理页）
6. 优化多线程架构，减少资源竞争

---

*本文档由 GitHub Copilot 根据代码仓库自动生成，如有疏漏请结合源代码进行修正。*
