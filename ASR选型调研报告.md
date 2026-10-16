# ASR 语音识别选型调研报告（2026-10）

> 背景：系统现行方案为阿里云 Paraformer-realtime-v2（2025 年选型）+ 百度 ASR 备选。
> 本报告调研 2026 年当前可选方案，覆盖「云端 API」与「树莓派端侧离线」两条路线，给出替换建议。
> 结论先行：**云端主链路换 qwen3-asr-flash-realtime（同厂商、改配置即可）；端侧离线选 SenseVoice-Small（sherpa-onnx），不要用 Whisper。**

---

## 1. 需求约束（智能魔镜场景）

- 语音短指令为主（查天气/时间/任务、闲聊），中文为主 + 英语，多语言（已不承诺日语）
- 端到端延迟目标 ≤5s；噪声环境（家庭）鲁棒性重要
- Pi 4 无 GPU、内存有限 → 端侧模型必须 CPU 可跑、≤250MB
- 成本敏感：个人项目，免费额度优先

## 2. 云端 API 对比（阿里云百炼为主）

| 模型 | 中文精度 | 实时流式 | 价格（国内） | 免费额度 | 备注 |
|---|---|---|---|---|---|
| **qwen3-asr-flash-realtime** ⭐ | 优（公开测试中文 3.97%、带口音中文 3.48%，优于 GPT-4o-Transcribe 15.72%/17.07%、Paraformer-v1/v2、豆包） | ✅ 实时版 | ¥0.00033/秒（≈¥1.19/小时） | 36,000 秒（10 小时） | 基于 Qwen3 基座，自动语种判别、抗噪强、支持热词/上下文定制 |
| qwen-audio-3.0/3.1-asr-flash-streaming | 旗舰（2026 迭代版） | ✅ | ¥0.00033/秒 | 有 | 更新的旗舰流式版，可视为 qwen3-asr-flash 的后继 |
| fun-asr-realtime（Fun-ASR 7.7B） | 良 | ✅ | $0.00009/秒 | 36,000 秒 | LLM 架构新方案；注意**商用 Fun-ASR 与开源 Paraformer 是两套完全不同的系统**（7.7B vs 220M） |
| paraformer-realtime-v2（现行） | 中 | ✅ | $0.000035/秒 | **无免费额度** | 2025 选型；CTC v2 抗噪有改进，但精度已被 Qwen3-ASR 全面超越 |
| 百度 ASR（备选现行） | 中 | ✅ | 按次计费 | 有限 | 精度与生态均不及百炼新模型 |

**关键发现**：qwen3-asr-flash-realtime 与现行方案同在百炼平台，切换只需改模型名与调用方式，SDK 不变；且价格同级情况下有 10 小时/月免费额度（现行 Paraformer 实时版无免费额度）。

## 3. 开源/端侧模型对比（普通话 CER，同口径数据来自 FireRedASR2S 仓库）

| 模型 | 参数量 | 普通话平均 CER | 端侧可行性 | 结论 |
|---|---|---|---|---|
| FireRedASR2（小红书） | 8.3B | **2.89%**（全场最优） | ❌ 需 32GB GPU | 精度天花板，但消费级设备跑不动 |
| Qwen3-ASR-1.7B | 1.7B | 3.76% | ❌ 需 6–8GB 显存，不支持纯 CPU | 精度好但**不适合树莓派**；且成熟度存疑（~148 个 open issues、有无限重复输出缺陷） |
| SenseVoice-Small（阿里） | 234M | ~3.0%（AISHELL） | ✅ sherpa-onnx ONNX 版 228MB，3 秒音频延迟仅 63ms，CPU 可跑 | **端侧首选**：非自回归架构比 Whisper 快 15 倍，附带情感/事件检测 |
| Paraformer-zh（开源 220M） | 220M | 1.95%（AISHELL，官方口径） | ✅ sherpa-onnx，RTF 0.014 极快 | 老将宝刀未老，端侧精度/速度均衡，工具链最成熟 |
| Fun-ASR-Nano | 800M | ~4.55% | ⚠️ 需 FunASR 工具包 | 与 SenseVoice 同门，端侧优势不明显 |
| Whisper large-v3 | 1550M | WenetSpeech meeting 达 18.87%，长音频幻觉严重 | ❌ CPU 慢 10 倍以上（RTF 0.37） | **中文场景不推荐**，仅作参照基线 |
| Moonshine | 27M | 中文 36.1%（训练数据仅 69.8 小时） | ✅ 34ms 延迟 | 中文不可用 |
| sherpa-onnx-streaming-zipformer 双语 | 40MB | 中 | ✅ 流式、最快 | 内存极紧时的备选 |

## 4. 推荐方案（双轨）

### 轨道 1：云端主链路（默认使用）
**paraformer-realtime-v2 → qwen3-asr-flash-realtime**
- 理由：同平台迁移成本≈0（改 `config.yaml` 模型名 + 调用适配）；精度显著提升（中文错误率约为原方案的一半以下量级）；10 小时/月免费额度；热词上下文定制可以把「背单词」「小镜」等自有词加进识别偏置
- 回退：保留百度 ASR 备选位不动；后续旗舰 qwen-audio-3.x-asr-flash-streaming 亦可平替

### 轨道 2：端侧离线（服务本地 Agent 的离线场景）
**SenseVoice-Small（sherpa-onnx ONNX 版，228MB）**
- 理由：被端侧选型文章明确列为「树莓派场景」推荐；63ms 级推理延迟 + 中文 CER ~3%；纯 CPU；非流式但对短指令场景无影响（现有 VAD 已做分段）
- 备选：内存紧张时用 sherpa-onnx-streaming-zipformer 双语版（40MB，流式）
- **明确不选**：Whisper（中文弱 + CPU 慢）、Qwen3-ASR/FireRedASR 本地部署（需 GPU）

## 5. 迁移成本与风险

| 项 | 评估 |
|---|---|
| 云端切换 | 低：同 SDK，改模型 ID；ASR 后端本就设计为可配置切换 |
| 端侧新增 | 中：Pi 需装 sherpa-onnx + 下载 ONNX 模型；与 VAD(torch) 并存需实测内存（SenseVoice ONNX 版无 torch 依赖，风险小） |
| 风险 | ① qwen3-asr 免费额度用尽后按秒计费（≈¥1.19/h，个人用量可忽略）② Qwen3-ASR 开源版缺陷不影响云端 API 版 ③ SenseVoice 无流式，长句场景延迟略增（本场景无影响） |

## 6. 与毕业设计材料的关系

任务书/开题报告当前写的是「接入阿里云 Paraformer 与百度语音识别双后端」。若采纳本报告：云端改为「Qwen3-ASR（Paraformer 备选）」、端侧补充「SenseVoice-Small 离线识别」一句即可——这反而强化了「端云协同」的技术叙事（云端高精度 + 端侧离线兜底），是论文的加分点。

## 7. 主要参考来源

- FireRedASR2S 仓库统一基准对比（掘金/CSDN 转载，2026）：FireRedASR2 2.89% / Qwen3-ASR 3.76% / Fun-ASR-Nano 4.55%；Whisper 中文短板数据
- 2026 商用 ASR 全景选型（peihuachen.github.io）：13 款商用产品 CER 横评、Whisper 长音频 20% 幻觉实测
- 阿里云百炼官方文档：qwen3-asr-flash-realtime / qwen-audio-3.x-asr-flash-streaming / fun-asr-realtime / paraformer-realtime-v2 价格与免费额度
- Qwen3-ASR-Flash 发布报道（2025-09）：中文 3.97%、带口音 3.48%，对比 GPT-4o-Transcribe 15.72%/17.07%
- ASR in 2025-2026 深度选型文（ruoqijin.com）：Qwen3-ASR 开源版 148 open issues、伪流式限制、商用 Fun-ASR ≠ 开源 Paraformer 的关键澄清
- pi-voicekit 端侧实测：paraformer-zh RTF 0.014 / sensevoice-small RTF 0.028 / whisper-turbo RTF 0.372
- sherpa-onnx 树莓派部署实战（CSDN，2025）：zipformer 40MB 流式 / SenseVoice 150MB 端侧方案
