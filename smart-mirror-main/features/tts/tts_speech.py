from features.common.config_loader import config
from features.common.file_manage import manage_audio_files
from features.common.utils import read_text_baidu
from features.common.log_loader import logger
from features.common.AudioPlayer import AsyncAudioPlayer
import asyncio
from features.common.globals import set_tts_state
from path_hub import temp_tts_path_abs
TAG=__name__
def tts_speech(text,which_tts=config['choose']['tts']):
    manage_audio_files(temp_tts_path_abs)
    set_tts_state(True)
    try:
        if which_tts=='tts_baidu':
            read_text_baidu(text)
        elif which_tts=="tts_huoshan":
            audio_player =AsyncAudioPlayer()
            try:
                result=asyncio.run(audio_player.speak(text))

            finally:
                audio_player.cleanup()
        else:
            logger.bind(tag=TAG).error("请检查yaml配置，选择正确的语音合成平台")
    finally:
        set_tts_state(False)

async def tts_speech_sync(text,which_tts=config['choose']['tts']):
    manage_audio_files(temp_tts_path_abs)
    set_tts_state(True)
    try:
        if which_tts=='tts_baidu':
            read_text_baidu(text)
        elif which_tts=="tts_huoshan":
            audio_player =AsyncAudioPlayer()
            try:
                result=await (audio_player.speak(text))

            finally:
                audio_player.cleanup()
        else:
            logger.bind(tag=TAG).error("请检查yaml配置，选择正确的语音合成平台")
    finally:
        set_tts_state(False)