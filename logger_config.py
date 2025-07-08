# logger_config.py
from loguru import logger
import logging
import sys

def setup_loguru():
    logger.remove()  # 移除默认的 handler

    # 添加彩色控制台输出
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>[{extra[tag]}]</cyan> | {message}",
        level="DEBUG"
    )

    return logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 获取对应的 loguru level
        level = logger.level(record.levelname).name if record.levelname in logger._core.levels else record.levelno

        # 获取原始日志消息
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
