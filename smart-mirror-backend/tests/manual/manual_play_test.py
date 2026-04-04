from features.common.AudioPlayer import AsyncAudioPlayer
import asyncio
async def tts_speech():
    audio_player =AsyncAudioPlayer()

    try:
        text='''Engineer Lin Xia's fingers froze on the holographic keyboard. The system alert was blinking red:
"孙中山原始声纹数据已替换为TTS合成版本（置信度99.98%）"
"不可能..." Her coffee cup shattered on the floor. 档案馆的火山引擎TTS系统日志显示，这段audio竟然是用她的admin权限在凌晨3:17生成的。更可怕的是——security cameras显示那个时间她根本不在现场。'''
        result= await audio_player.speak(text)
    finally:
        audio_player.cleanup()





