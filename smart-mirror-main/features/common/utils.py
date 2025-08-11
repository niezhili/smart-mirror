from collections import defaultdict
import audioop
import os
import tempfile
import time
import threading
import wave
import pyaudio
import pyttsx3
import glob
import yaml
from features.tts.tts_huoshan import text_to_speech
import shutil
from aip import AipSpeech
from datetime import datetime
from pathlib import Path
import cv2
from loguru import logger
import pygame
from features.common.text_cutter import text_cutter
from features.asr.asr_paraformer import speech_to_text_paraformer
from features.common.globals import is_tts_working,set_recording_requested,set_tts_state
TAG = __name__


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config/config.yaml")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    Config = yaml.safe_load(f)
config=Config

# Baidu API credentials
APP_ID = config['tts']['tts_baidu']['baidu_app_id']
API_KEY = config['tts']['tts_baidu']['baidu_api_key']
SECRET_KEY = config['tts']['tts_baidu']['baidu_secret_key']


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config/config.yaml")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)


# def tts_speech(text: str, output_dir: str = "temp_tts"):
#     which_tts=config["choose"]["tts"]
#     text_cutted=text_cutter(text)
#     if text_cutted==[]:
#         return ""
#     for text_i in text_cutted:
#         if which_tts=="tts_huoshan":
#             tts_huoshan(text_i)
#         elif which_tts=="tts_baidu":
#             tts_baidu(text_i)
#         else:
#             logger.bind(tag=TAG).error("请检查yaml配置，选择正确的语音合成平台")


def tts_huoshan(text: str, output_dir: str = "temp_tts"):
    try:
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"tts_{int(time.time())}.wav")

        # 增加调试日志
        logger.info(f"开始合成语音，文本长度：{len(text)}")
        result = text_to_speech(text, output_file=output_file, voice_type="default")

        if not os.path.exists(output_file):
            logger.error("火山引擎未生成有效音频文件")
            return None

        logger.success(f"音频文件已生成：{output_file} ({os.path.getsize(output_file)} bytes)")
        return output_file

    except Exception as e:
        logger.error(f"语音合成失败：{str(e)}")
        return None


# def tts_huoshan(text: str, output_dir: str = "temp_tts"):
#     """
#     //qishibushi
#     huoshan_tts
#     合成语音、保存并播放，同时维护 temp_tts 文件夹中的文件数量不超过 15 个。
#     使用 .wav 格式 + pygame 播放，适用于树莓派。
#     """
#     # 设置 TTS 状态为 True
#     # set_tts_state(True)
#     # 创建 temp_tts 文件夹,获取文件名
#     os.makedirs(output_dir, exist_ok=True)
#     timestamp = datetime.now().strftime("tts_huoshan_%Y%m%d_%H%M%S")
#     output_file = os.path.join(output_dir, f"{timestamp}.wav")  # 确保输出为 WAV 格式
#     output_file = os.path.abspath(output_file)
#     # 根据语言选择音色
#     language = detect(text)
#     if language == "ja":
#         # 日语
#         text_to_speech(text, output_file=output_file,voice_type=config['tts']['tts_huoshan']['voice_type']["ja"])
#     elif language == "de":
#         # 德语
#         text_to_speech(text, output_file=output_file,voice_type=config['tts']['tts_huoshan']['voice_type']["de"])
#     elif language == "fr":
#         # 法语
#         text_to_speech(text, output_file=output_file,voice_type=config['tts']['tts_huoshan']['voice_type']["fr"])
#     else:
#         # 默认音色
#         text_to_speech(text, output_file=output_file,voice_type=config['tts']['tts_huoshan']['voice_type']["default"])
#
#     return output_file
    # manage_audio_files(output_dir)
    # logger.bind(tag=TAG).info("正在播放音频...")
    # try:
    #     play_audio_file(output_file)
    #     logger.bind(tag=TAG).info("播放完成。")
    #     set_tts_state(False)
    # except Exception as e:
    #     logger.bind(tag=TAG).error(f"播放失败: {str(e)}")
    #     set_tts_state(False)


def play_audio_file(file_paths, skip_last_frames=0):
    """
    使用 pygame 播放 .wav 音频文件（支持树莓派）
    支持跳过最后几帧的播放

    参数:
        file_paths: 可以是字符串（单个文件路径）或列表（多个文件路径）
        skip_last_frames: 要跳过的最后帧数（默认为0）
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]  # 转换为列表统一处理

    try:
        pygame.mixer.init(frequency=24000, size=-16, channels=2, buffer=4096)

        for file_path in file_paths:
            try:
                # 加载音频文件并获取信息
                sound = pygame.mixer.Sound(file_path)
                length = sound.get_length()  # 获取音频总长度（秒）

                if skip_last_frames > 0:
                    # 计算要跳过的秒数（假设44100Hz采样率）
                    skip_seconds = skip_last_frames / 24000.0
                    # 确保不会跳过整个音频
                    play_length = max(0.1, length - skip_seconds)
                else:
                    play_length = length

                logger.bind(tag=TAG).info(
                    f"正在播放: {file_path} (总长度: {length:.2f}s, 实际播放: {play_length:.2f}s)")

                # 播放音频
                channel = sound.play()

                # 等待播放完成（减去跳过的部分）
                start_time = time.time()
                while time.time() - start_time < play_length and channel.get_busy():
                    pygame.time.delay(10)

                # 立即停止播放（确保跳过最后部分）
                channel.stop()

            except Exception as e:
                logger.bind(tag=TAG).error(f"播放 {file_path} 时出错: {str(e)}")
                continue  # 继续播放下一个文件

    except Exception as e:
        logger.bind(tag=TAG).error(f"音频播放初始化失败: {str(e)}")
    finally:
        # 确保pygame资源被正确释放
        try:
            pygame.mixer.quit()
        except:
            pass


# def play_audio_file(file_path):
#     """
#     huoshan
#     使用 pygame 播放 .wav 音频文件（支持树莓派）
#     """
#     try:
#         pygame.mixer.init()
#         sound = pygame.mixer.Sound(file_path)
#         sound.play()
#
#         # 等待播放完成
#         while pygame.mixer.get_busy():
#             pygame.time.delay(1)
#     except Exception as e:
#         logger.bind(tag=TAG).error(f"播放音频时出错: {str(e)}")
#     finally:
#         # 确保pygame资源被正确释放
#         try:
#             pygame.mixer.quit()
#         except:
#             pass


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



def create_directory_if_not_exists(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.bind(tag=TAG).info(f"Created directory: {directory}")


def copy_image_to_directory(image_path: str, target_dir: str):
    try:
        filename = os.path.basename(image_path)
        new_path = os.path.join(target_dir, filename)
        shutil.copy2(image_path, new_path)
        return new_path
    except Exception as e:
        logger.bind(tag=TAG).error(f"Error copying {image_path}: {str(e)}")
        return None


def _draw_face_annotations(frame, top, right, bottom, left, display_text):
    """Draw stable bounding box and text for detected faces"""
    # Calculate box thickness based on frame size
    thickness = max(1, min(2, int(frame.shape[1] / 640)))

    # Draw anti-aliased rectangle around the face
    cv2.rectangle(
        frame,
        (left, top),
        (right, bottom),
        (0, 255, 0),
        thickness,
        cv2.LINE_AA
    )

    # Calculate text background rectangle size
    text_size = cv2.getTextSize(
        display_text,
        cv2.FONT_HERSHEY_DUPLEX,
        0.6,
        1
    )[0]

    # Draw semi-transparent background for text
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (left, bottom - 35),
        (right, bottom),
        (0, 255, 0),
        cv2.FILLED
    )
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    # Add name text with anti-aliasing
    cv2.putText(
        frame,
        display_text,
        (left + 6, bottom - 6),
        cv2.FONT_HERSHEY_DUPLEX,
        0.6,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )


def tts_baidu(
        text,
        baidu_app_id=APP_ID,
        baidu_api_key=API_KEY,
        baidu_secret_key=SECRET_KEY,
        temp_audio_dir='temp_tts'
):
    """
    Convert text to speech using Baidu TTS and play the audio.

    Args:
        text (str): Text to be converted to speech.
        app_id (str): Baidu APP ID.
        api_key (str): Baidu API Key.
        secret_key (str): Baidu Secret Key.
        temp_audio_dir (str): Directory to save temporary audio files.
        :param temp_audio_dir: temporary audio directory
        :param baidu_secret_key: baidu secret key
        :param baidu_api_key: baidu api key
        :param text: text to be read
        :param baidu_app_id: baidu app id
    """
    set_tts_state(True)

    # Check if the credentials are not None
    if not all([baidu_app_id, baidu_api_key, baidu_secret_key]):
        raise ValueError("百度 API 凭证设置不正确.")

    # Initialize Baidu Speech Client
    client = AipSpeech(baidu_app_id.strip(), baidu_api_key.strip(), baidu_secret_key.strip())

    # Create temp directory if it doesn't exist
    temp_audio_path = Path(temp_audio_dir)
    temp_audio_path.mkdir(exist_ok=True)

    # Synthesize speech
    result = client.synthesis(text, 'zh', 1, {
        'spd': 5,  # Speed
        'pit': 5,  # Pitch
        'vol': 5,  # Volume
        'per': 4,  # Voice type
        'aue': 6   # Audio format : 6 for WAV
    })

    # Check if synthesis was successful
    if not isinstance(result, dict):
        # Save the audio to a temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_file = temp_audio_path / f'tts_baidu_{timestamp}.wav'
        with open(temp_file, 'wb') as f:
            f.write(result)

        manage_audio_files(temp_audio_dir)
        # play audio
        logger.bind(tag=TAG).info("正在播放音频...")
        try:
            play_audio_file(str(temp_file))
            logger.bind(tag=TAG).info("播放完成。")
            set_tts_state(False)

        except Exception as e:
            logger.bind(tag=TAG).error(f"播放失败: {str(e)}")
            set_tts_state(False)

    else:
        logger.bind(tag=TAG).error("语音合成错误。",result)
        set_tts_state(False)





def user_speech_recognition(timeout=30) -> str:
    # speech_recognition = RecognizeSpeech()
    # recognized_text = speech_recognition.recognize_from_microphone()

    recognized_text=audio_to_text(timeout)
    return recognized_text


# Update the listening and reading of data

def record_audio_until_silence(timeout=30):  # 添加超时参数（单位：秒）
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    SILENCE_THRESHOLD = 300  # 静音阈值（根据实际环境调整）
    SILENCE_DURATION = 1.5  # 检测到静默后停止录音的持续时间
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("等待语音输入...")

    # --- 新增超时逻辑 ---
    start_time = time.time()
    max_recording_time = 120  # 最大录音时间
    # -------------------

    frames = []
    silent_chunks = 0
    max_silent_chunks = int(SILENCE_DURATION * RATE / CHUNK)

    try:
        # 第一阶段：等待语音开始
        while True:
            data = stream.read(CHUNK)
            rms = audioop.rms(data, 2)
            if rms >= SILENCE_THRESHOLD:
                # logger.bind(tag=TAG).info("Voice detected")
                logger.bind(tag=TAG).info("倾听中...")
                break
            # --- 检查超时 ---
            if time.time() - start_time > timeout:
                logger.bind(tag=TAG).warning("录音超时：未检测到语音输入")
                return None
            # -----------------

        # 第二阶段：录音直到静默
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            rms = audioop.rms(data, 2)

            if rms < SILENCE_THRESHOLD:
                silent_chunks += 1
                if silent_chunks > max_silent_chunks:
                    # 静默足够长，结束录音
                    break
            else:
                silent_chunks = 0

            # --- 检查最大录音时间 ---
            if time.time() - start_time > max_recording_time:
                logger.bind(tag=TAG).warning("达到最大录音时间120s，强制结束")
                break
            # -------------------------

        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
            filename = tmpfile.name
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(frames))
            # logger.bind(tag=TAG).info(f"Speech segment saved to: {filename}")
            return filename

    except KeyboardInterrupt:
        logger.bind(tag=TAG).info("Stopped listening.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
def read_text_baidu(text):
    logger.bind(tag=TAG).warning("read_text_baidu模块更名为tts_baidu,强烈建议使用统一接口tts_speech")
    tts_baidu(text)
    # tts_speech(text)
def speech_to_text(audio):
    choose_asr=config['choose']['asr']
    if choose_asr=='asr_baidu':
        return speech_to_text_baidu(audio)
    elif choose_asr=="asr_paraformer":
        result=speech_to_text_paraformer(
            audio_file_path=audio,
            api_key=config['asr']['asr_paraformer']['dashscope.api_key'],
            language_hints=config['asr']['asr_paraformer']['language_hints'],
            model=config['asr']['asr_paraformer']['model']
        )
        return result
    else:
        logger.bind(tag=TAG).warning("请检测yaml配置，asr名称错误")
        return None

def speech_to_text_baidu(audio):
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    with open(audio, "rb") as f:
        audio_data = f.read()
    result = client.asr(audio_data, "wav", 16000, {"dev_pid": 1537})  # 1537 for Mandarin
    if "result" in result:
        return result["result"][0]
    else:
        logger.bind(tag=TAG).warning("Could not convert audio to text.")
        # print("Error in STT:", result)
        return None


# Text-to-Speech (TTS)
def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty("voice", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ZH-CN_HUIHUI_11.0")
    engine.setProperty("rate", 150)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def text_to_speech_chinese(text):
    t = threading.Thread(target=speak_text, args=(text,))
    t.start()
    t.join(timeout=10)  # Wait 10 seconds max

    if t.is_alive():
        logger.bind(tag=TAG).warning("Speech timed out. Something went wrong.")
        # print("⚠️ Speech timed out. Something went wrong.")
        # Optional: Kill or cleanup logic here
        return True
    else:
        logger.bind(tag=TAG).info("Text:", text)
        print("✅ Done speaking.")


def audio_to_text(timeout=30):
    # 带超时的语音转文字
    # 判断tts是否正在工作
    while is_tts_working():
        time.sleep(0.1)

    # if(is_tts_working()):
    #     set_recording_requested(True)
    #     return ""

    audio_file = record_audio_until_silence(timeout=timeout)
    if not audio_file:
        return ""

    text = speech_to_text(audio_file)
    if text:
        logger.bind(tag=TAG).info("识别到文本:", text)
        return text
    else:
        return ""

def load_known_faces_from_folder(folder_path):
    """
    Scans the given folder and maps each image file to a person name based on the file name.
    Example: Joseph.jpg -> person_name = "Joseph"
    Returns a dictionary: { "Joseph": ["known_faces/Joseph.jpg"], ... }
    """
    folder = Path(folder_path)
    image_paths_by_person = defaultdict(list)

    for image_path in folder.glob("*.jpg"):
        person_name = image_path.stem  # e.g., Joseph from Joseph.jpg
        image_paths_by_person[person_name].append(str(image_path))

    return image_paths_by_person

