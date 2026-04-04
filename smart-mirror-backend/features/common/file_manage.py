import glob
import os
from features.common.log_loader import logger
TAG=__name__
def manage_audio_files(directory: str, max_files: int = 15):
    """
    管理指定目录下的音频文件数量，保留最新的 max_files 个文件。
    """
    files = glob.glob(os.path.join(directory, "*.wav"))  # 改为 .wav
    if len(files) > max_files:
        files.sort(key=os.path.getmtime)
        for file in files[:len(files) - max_files]:
            try:
                os.remove(file)
                logger.bind(tag=TAG).info(f"已删除旧音频：{file}")

            except Exception as e:
                logger.bind(tag=TAG).error(f"无法删除 {file}: {str(e)}")

