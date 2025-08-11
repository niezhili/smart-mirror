import os
from features.tts.tts_huoshan import text_to_speech_huoshan
import time
from path_hub import temp_tts_path_abs
os.makedirs(temp_tts_path_abs, exist_ok=True)
audio_path = os.path.join(temp_tts_path_abs,f"tts_huoshan_{int(time.time())}.wav")
text_to_speech_huoshan("hello world,",audio_path)