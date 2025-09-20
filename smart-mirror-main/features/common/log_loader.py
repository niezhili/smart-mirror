from loguru import logger
import sys
from log.location import logs_path

# 确保日志目录存在
logs_path.mkdir(exist_ok=True)

# 移除默认处理器
logger.remove()

# 添加：控制台输出（stdout），带颜色、异步、自定义格式
logger.add(
    sink=sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>[{extra[tag]}]</cyan> | {message}",
    level="INFO",
    enqueue=True,  # 异步写入（推荐）
    filter=lambda record: True  # 可选：自定义过滤
)

# 添加：文件输出（自动异步，rotation, retention）
logger.add(
    sink=str(logs_path / "app_{time:YYYYMMDD}.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{extra[tag]}] | {message}",
    level="INFO",
    rotation="1 day",
    retention="7 days",
    encoding="utf-8",
    enqueue=True,  # 文件写入异步化（重要！）
)