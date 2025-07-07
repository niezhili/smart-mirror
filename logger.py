from loguru import logger
import sys

# 配置日志格式，支持颜色和 tag 字段
logger.remove()  # 移除默认的 handler
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>[{extra[tag]}]</cyan> | {message}"
)

# 使用 tag 输出日志
logger.bind(tag="APP").info("应用启动")
logger.bind(tag="DEBUG").debug("这是一个调试信息")
logger.bind(tag="ERROR").error("发生了一个错误")
logger.bind(tag="WARNING").warning("警告信息")
logger.bind(tag="SUCCESS").success("操作成功")
