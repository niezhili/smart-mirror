from loguru import logger
import sys
from logs.location import logs_path
logs_path.mkdir(exist_ok=True)
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>[{extra[tag]}]</cyan> | {message}"
)
# 文件输出（保留颜色代码）
logger.add(
    str(logs_path / "app_{time:YYYYMMDD}.logs"),
    rotation="1 day",
    retention="7 days",
    encoding="utf-8",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>[{extra[tag]}]</cyan> | {message}",
    enqueue=True
)

