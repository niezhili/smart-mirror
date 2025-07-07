from loguru import logger
import sys
from pathlib import Path
from datetime import datetime

class LoggerConfig:
    _loggers = {}

    @staticmethod
    def setup_logger(logger_name: str, log_dir: str = 'logs'):
        """
        创建或获取一个带 tag 支持的日志器，支持彩色控制台和文件日志
        """
        if logger_name in LoggerConfig._loggers:
            return LoggerConfig._loggers[logger_name]

        log_dir = Path(log_dir)
        log_dir.mkdir(exist_ok=True, parents=True)

        # 生成日志文件名：logger_name_YYYYMMDD.log
        log_file = log_dir / f"{logger_name}_{datetime.now():%Y%m%d}.log"

        # 移除默认 handler
        logger.remove()

        # 添加控制台输出（INFO+，彩色）
        logger.add(
            sys.stdout,
            level="INFO",
            colorize=True,
            format="<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> | {message}"
        )

        # 添加文件输出（DEBUG+，无颜色）
        logger.add(
            str(log_file),
            level="DEBUG",
            rotation="1 day",
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
        )

        # 将 logger 包装成可绑定 tag 的方式
        bound_logger = logger.bind(tag=logger_name)
        LoggerConfig._loggers[logger_name] = bound_logger
        return bound_logger

    @staticmethod
    def handle_error(bound_logger, error_type: str, error_msg: str, exception: Exception = None):
        """
        统一错误处理方法，记录错误信息并返回字符串
        """
        error_detail = f"{error_type}: {error_msg}"
        if exception:
            error_detail += f" - {str(exception)}"

        bound_logger.error(error_detail)
        return error_detail

    @staticmethod
    def cleanup_old_logs(log_dir: str, days_to_keep: int = 7):
        """
        清理指定目录下超过保留天数的日志文件
        """
        log_dir = Path(log_dir)
        if not log_dir.exists():
            return

        current_time = datetime.now().timestamp()
        for log_file in log_dir.glob("*.log"):
            file_age = current_time - log_file.stat().st_mtime
            if file_age > days_to_keep * 24 * 3600:
                try:
                    log_file.unlink()
                except Exception as e:
                    print(f"清理日志文件失败: {log_file} - {e}")
