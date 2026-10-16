# 智能魔镜 × LazyTODO 集成方案

> 版本 v1.0 · 2026-10-15 · 状态：范围已与用户确认，待开发
> 前置文档：`PRD.md`（智能魔镜）、`LazyTODO-PRD.md` v0.5、`LazyTODO-技术细节总结.md` v0.1.0

---

## 1. 一句话定位

把 LazyTODO 的"主功能"（妙记同步 → AI 提取 → 任务提醒 → 打卡）搬进树莓派智能魔镜：**镜子成为任务的展示、语音查询与提醒终端，树莓派同时承担 LazyTODO 的服务端 worker**；手机 App 保持不动，继续作为待确认队列的确认入口。

## 2. 已确认的设计决策（用户拍板）

| # | 决策点 | 结论 |
|---|---|---|
| 1 | 妙记拉取与 AI 提取由谁负责 | **树莓派**（LazyTODO 主功能放入 Pi） |
| 2 | Pi 的角色边界 | **服务端 worker**：同步+提取+提醒，读写现有 WorkBuddy 云库；**不替代云、不本地建库**，手机 App 零改动 |
| 3 | 到点提醒方式 | **有人时语音播报 + 镜面横幅；无人时仅屏幕常驻显示**（复用 PIR/人脸检测结果） |
| 4 | 镜面展示范围 | **人脸识别通过后显示"我的今日任务"**（时间轴 + 待办），不区分多人（当前单用户） |
| 5 | 语音操作范围 | **查询 + 打卡完成**（"今天有什么事""帮我打卡背单词"），不做语音新建任务 |
| 6 | 录音来源 | **仅录音豆 → 飞书妙记**；镜子麦克风现场录音本期不进提取链路 |
| 7 | 飞书接入方式 | 用户自行创建**飞书自建应用**，开通妙记只读权限，app_id/app_secret 配置到 Pi |

## 3. 架构

```
录音豆 ──蓝牙/网络──▶ 飞书妙记（转写完成）
                          │
                 ① 轮询拉取（自建应用 API，增量游标）
                          │
┌─────────────────────────▼──────────────────────────────┐
│ 树莓派 smart-mirror-backend（新增 lazytodo 域）           │
│  feishu_sync.py    妙记轮询 worker（增量游标/失败退避）     │
│  todo_extract.py   复用现有 LLM 适配器做四分类提取          │
│  todo_service.py   任务查询/打卡（读写 LazyTODO 云库）      │
│  todo_reminder.py  到点检查 + 语音播报/横幅触发             │
└───────┬──────────────────────────────┬─────────────────┘
        │ ② 写入 queue_items / 读 items │ ③ 语音查询/打卡（现有 VAD→ASR→LLM 链路新增意图）
        ▼                              ▼
   WorkBuddy 云库（LazyTODO 现有      镜面交互层（人脸识别 → MagicMirror²
   6 张表，RLS owner-only，结构     MMM-LazyTodo 模块：任务列表/横幅）
   不动）                           │
        ▲                          │
        └── ④ 手机 LazyTODO App：确认待确认队列（现有流程，不动）
```

## 4. 新增模块设计

### 4.1 后端（smart-mirror-backend/features/lazytodo/）

| 文件 | 职责 | 关键点 |
|---|---|---|
| `feishu_client.py` | 飞书自建应用鉴权（tenant_access_token 自动续期）+ 妙记列表/转写拉取 | token 内存缓存过期前刷新；限流退避 |
| `feishu_sync.py` | 妙记轮询 worker（独立线程）：增量游标 `last_synced_at`、`minute_token` 去重、仅处理转写完成的妙记 | 轮询周期：活跃时段 15 min / 夜间 1 h；失败指数退避 15min→30min→1h |
| `todo_extract.py` | 转写文本 → 四分类提取（reminder/event/todo/note） | 复用现有 LLM 适配器（Qwen/DeepSeek 可切换）；few-shot 纠错复用云库 `ai_feedback` 最近 10 条；结果写 `queue_items(pending)` |
| `todo_service.py` | 云库读写封装：今日任务查询、打卡（PATCH status/done_at）、连击 bumpStreak 语义 | PostgREST 协议复用 LazyTODO 已验证的过滤/RLS 规则（**永不发送 owner_id**；需在 Pi 侧持有用户登录态，见 §6 风险②） |
| `todo_reminder.py` | 到点检查 worker：每分钟对比 `items.remind_at/start_at`，到点且未完成 → 触发提醒 | 有人（PIR/人脸命中）才 TTS 播报 + 横幅；无人仅 UI 常驻；完成后撤横幅 |

### 4.2 语音链路扩展（现有 main.py 主循环）

新增意图：`query_todo`（今天有什么事/我还有什么没做）→ 调 `todo_service` 拉今日未完成 → TTS 播报摘要（按时间排序，最多 5 条）；`checkin_todo`（打卡/完成了XX）→ LLM 匹配任务标题 → 打卡 + TTS 确认"已打卡，连击 N 天"。

### 4.3 前端（smart-mirror-frontend 新模块 MMM-LazyTodo）

- 触发：人脸识别成功事件 → 拉取今日时间轴 + 待办，展示 15s/常驻至离开；
- 展示：时间轴（时间 + 标题 + 完成圈，完成态灰化删除线）+ 待办分组 + 待确认队列角标；
- 到点提醒横幅：深色悬浮卡"背单词 · 未完成"，完成后消失；
- 数据源：Pi 后端新增 HTTP 端点（Flask，:8080 现有服务扩展 `/api/lazytodo/today`、`/api/lazytodo/checkin`）。

## 5. 开发阶段

| 阶段 | 内容 | 验收 |
|---|---|---|
| P1 任务展示+打卡 | todo_service + MMM-LazyTodo + 语音查询/打卡 | 镜前识别人脸见今日任务；语音打卡成功且手机端同步 |
| P2 到点提醒 | todo_reminder + 横幅 + 有人语音播报 | 到点（有人在）10s 内播报；无人时仅横幅 |
| P3 妙记同步 | feishu_client + feishu_sync + todo_extract | 录音结束后 ≤25 min 出现在待确认队列；手机确认落地正常 |

## 6. 风险与前置条件

1. **妙记 API 权限与额度**：需确认自建应用可读 `minutes` 转写（LazyTODO POC 结论：无转写完成事件推送，只能轮询）；若免费额度不可读转写，降级为拉源音频 → Gemini Flash（LazyTODO PRD §9 风险①）。
2. **Pi 侧用户登录态**：云库 RLS 按 `auth.uid()` 隔离，Pi 的 worker 需要以该用户身份的 access_token（可复用 OTP 登录流程一次性获取并持久化 refresh_token，过期自动续期）。
3. **依赖网络**：整个链路依赖外网（妙记/LLM/云库）；离线时提醒退化为仅屏幕显示。
4. **前置动作（用户）**：创建飞书自建应用 → 开通妙记只读权限 → 提供 app_id/app_secret；确保录音豆已绑定妙记上传。

## 7. 与毕业设计的关系

本集成可作为毕设"后续规划"中的系统扩展点（多源信息接入 + 端云协同应用案例）；若选题确认，可将 P1/P2 内容写入论文的"系统扩展与应用验证"章节。不改动已交付的任务书/开题报告正文，仅备查。
