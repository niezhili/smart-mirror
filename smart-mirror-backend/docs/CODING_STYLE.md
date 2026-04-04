# Smart Mirror 开发规范
## 1. 项目结构规范

### 1.1 目录结构
```

smart-mirror-backend/
├── config/              # 配置文件
├── docs/                # 文档
├── features/            # 功能模块
│   ├── asr/             # 语音识别
│   ├── common/          # 公共组件
│   ├── face_recognition/ # 人脸识别
│   ├── llm/             # 大语言模型
│   ├── tts/             # 文字转语音
│   ├── vad/             # 语音活动检测
│   └── weather/         # 天气服务
├── home_control/        # 家居控制
├── logs_AND_location/   # 日志和路径管理
├── tests/               # 测试文件
└── known_faces/         # 已知人脸图片
```
### 2.2 模块设计原则
- 每个功能模块应独立封装在单独的目录中
- 模块内部应包含功能实现文件和辅助文件
- 公共组件放在 `features/common/` 目录下
- 每个模块应提供清晰的接口供其他模块调用

## 3. 日志规范

### 3.1 日志使用
- 使用 `loguru` 库进行日志记录
- 每个模块需引入 `features.common.log_loader` 中的 `logger` 对象
- 日志必须包含模块标签，使用 `logger.bind(tag=TAG)` 方式

```
python
from features.common.log_loader import logger

TAG = __name__

# 记录日志示例
logger.bind(tag=TAG).info("这是一条信息日志")
logger.bind(tag=TAG).error("这是一条错误日志")
```
### 3.2 日志级别
- DEBUG: 调试信息，仅在调试时使用
- INFO: 一般信息，用于记录程序运行状态
- WARNING: 警告信息，程序可以继续运行
- ERROR: 错误信息，功能无法正常执行
- CRITICAL: 严重错误，程序可能无法继续运行

## 4. 配置管理规范

### 4.1 配置文件
- 所有配置项统一保存在 `config/config.yaml` 文件中
- 配置项应有清晰的注释说明用途
- 敏感信息（如API密钥）不应提交到代码仓库

### 4.2 配置使用
- 使用 `features/common/config_loader.py` 加载配置
- 在模块中通过 `from features.common.config_loader import config` 引入

```
python
from features.common.config_loader import config

# 使用配置项
api_key = config['api']['key']
```
## 5. 异常处理规范

### 5.1 异常捕获
- 对可能出错的代码块进行异常捕获
- 记录异常信息便于调试
- 合理处理异常，避免程序崩溃

```
python
try:
    # 可能出错的代码
    result = some_operation()
except SpecificException as e:
    logger.bind(tag=TAG).error(f"操作失败: {e}")
    # 合理的异常处理
```
### 5.2 异常抛出
- 自定义异常应继承自标准异常类
- 异常信息应清晰描述错误原因

## 6. 多线程规范

### 6.1 线程使用
- 使用 `threading` 模块创建和管理线程
- 涉及共享资源时使用线程锁
- 避免线程间死锁问题

```
python
import threading

# 创建线程锁
global_lock = threading.Lock()

# 使用线程锁
with global_lock:
    # 访问共享资源
    shared_resource = new_value
```
### 6.2 线程安全
- 对共享变量的访问需要加锁保护
- 使用队列（Queue）进行线程间通信
- 避免在多线程环境中直接操作UI

## 7. 测试规范

### 7.1 单元测试
- 为关键功能编写单元测试
- 测试文件放在 `tests/` 目录下
- 测试文件命名以 `test_` 开头

### 7.2 测试覆盖
- 核心业务逻辑应有测试覆盖
- 边界条件和异常情况需要测试
- 定期运行测试确保代码质量

## 8. Git提交规范

### 8.1 提交信息格式
```

<type>(<scope>): <subject>

<body>

<footer>
```
### 8.2 提交类型
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

### 8.3 提交示例
```

feat(face_recognition): 添加人脸识别超时功能

增加了人脸识别的超时机制，避免程序长时间等待

Closes #123

```
### 8.4 提交说明
- 先提交到beta，审核后合并dev
- dev稳定后进入main