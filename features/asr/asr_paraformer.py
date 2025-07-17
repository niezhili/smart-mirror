import dashscope
from dashscope.audio.asr import Recognition
from http import HTTPStatus
from loguru import logger
import sys
TAG = __name__
logger.remove()  # 移除默认的 handler
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>[{extra[tag]}]</cyan> | {message}"
)


def speech_to_text_paraformer(
    audio_file_path: str,
    api_key: str = "",
    model: str = 'paraformer-realtime-v2',
    sample_rate: int = 16000,
    language_hints: list = None
) -> str :
    """
    使用 DashScope 的语音识别接口将音频文件转为文字。

    参数:
        audio_file_path (str): 音频文件路径。
        api_key (str): DashScope API 密钥。
        model (str): 使用的语音识别模型。
        sample_rate (int): 音频采样率。
        language_hints (list): 语言提示列表。

    返回:
        str or None: 识别成功返回文本，失败返回 ""。
    """
    if not api_key:
        logger.bind(tag=TAG).warning("API Key is required for DashScope.")
        return ""

    # 设置 API Key
    dashscope.api_key = api_key


    # 初始化识别器
    recognition = Recognition(
        model=model,
        format="wav",
        sample_rate=sample_rate,
        language_hints=language_hints or ['zh', 'en'],
        callback=None
    )

    # 调用语音识别
    raw_result = recognition.call(audio_file_path)

    if raw_result.status_code == HTTPStatus.OK:
        result = raw_result.get_sentence()
        if not result:
            return ""
        else:
            return result[0]['text']
    else:
        logger.bind(tag=TAG).warning(f"Error in DashScope STT: {raw_result.message}")
        return ""