import os
import tempfile
from features.tts.tts_huoshan import text_to_speech
from loguru import logger
TAG = __name__

def system_self_check():

    test_text = "这是一条测试语音合成消息"
    temp_output = os.path.join(tempfile.gettempdir(), "tts_test.wav")

    try:
        logger.bind(tag=TAG).info("开始执行火山引擎 TTS 自检...")
        logger.bind(tag=TAG).info(f"尝试合成语音: '{test_text}' -> {temp_output}")

        # 调用火山 TTS 接口
        text_to_speech(test_text, output_file=temp_output)

        # 检查输出文件是否存在
        if os.path.exists(temp_output):
            logger.bind(tag=TAG).info("✅ TTS 合成成功，音频文件已生成")
            logger.bind(tag=TAG).info(f"🗑️ 清理测试文件: {temp_output}")
            os.remove(temp_output)
        else:
            logger.bind(tag=TAG).error("❌ TTS 合成失败，未生成音频文件")
            return False

        return True

    except Exception as e:
        logger.bind(tag=TAG).error(f"❌ TTS 自检异常: {str(e)}")
        return False


if __name__ == "__main__":
    result = system_self_check()
    print("系统自检结果:", "通过 ✅" if result else "失败 ❌")
