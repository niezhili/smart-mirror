
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

# def tts_to_voice(rext: str, output_dir: str = "temp_tts"):
#     tts_platform=
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config/config.yaml")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

def tts_speech(text: str, output_dir: str = "temp_tts"):
    if config["choose"]["tts"]=="tts_huoshan":
        # logger.bind(tag=TAG).error("火山火山火山")
        tts_huoshan(text)
    elif config["choose"]["tts"]=="tts_baidu":
        # logger.bind(tag=TAG).error("百度")
        tts_baidu(text)
    else:
        logger.bind(tag=TAG).error(" 请检查yaml配置，选择正确的语音合成平台")
def tts_huoshan(text: str, output_dir: str = "temp_tts"):
    """
    //qishibushi
    huoshan_tts
    合成语音、保存并播放，同时维护 temp_tts 文件夹中的文件数量不超过 15 个。
    使用 .wav 格式 + pygame 播放，适用于树莓派。
    """
    set_tts_state(True)
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{timestamp}.wav")  # 确保输出为 WAV 格式
    output_file = os.path.abspath(output_file)

    print(f"正在合成语音：{text}")
    text_to_speech(text, output_file=output_file)
    logger.bind(tag=TAG).info(f"已保存音频至：{output_file}")

    manage_audio_files(output_dir)

    print("正在播放音频...")
    try:
        play_audio_file(output_file)
        print("播放完成。")
        set_tts_state(False)

    except Exception as e:
        logger.bind(tag=TAG).error(f"播放失败: {str(e)}")
        set_tts_state(False)

def play_audio_file(file_path):
    """
    huoshan
    使用 pygame 播放 .wav 音频文件（支持树莓派）
    """
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.play()

    # 等待播放完成
    while pygame.mixer.get_busy():
        pygame.time.delay(100)


def manage_audio_files(directory: str, max_files: int = 15):
    """
    huoshan
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
        temp_audio_dir='temp_audio'
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
        raise ValueError("Baidu API credentials are not set properly.")

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
        temp_file = temp_audio_path / f'tts_{timestamp}.wav'
        with open(temp_file, 'wb') as f:
            f.write(result)

        manage_audio_files(temp_audio_dir)  # 使用已有的函数管理文件
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
        logger.bind(tag=TAG).error("Error in speech synthesis",result)
        set_tts_state(False)





def user_speech_recognition(timeout=5) -> str:
    # speech_recognition = RecognizeSpeech()
    # recognized_text = speech_recognition.recognize_from_microphone()

    recognized_text=audio_to_text(timeout)
    return recognized_text


# Update the listening and reading of data

def record_audio_until_silence(timeout=5):  # 添加超时参数（单位：秒）
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    SILENCE_THRESHOLD = 500  # 静音阈值（根据实际环境调整）
    SILENCE_DURATION = 1.5  # 检测到静默后停止录音的持续时间
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Listening for voice...")

    # --- 新增超时逻辑 ---
    start_time = time.time()
    max_recording_time = timeout  # 最大录音时间
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
                logger.bind(tag=TAG).info("正在倾听...")
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
                logger.bind(tag=TAG).warning("达到最大录音时间，强制结束")
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
            logger.bind(tag=TAG).info(f"Speech segment saved to: {filename}")
            return filename

    except KeyboardInterrupt:
        logger.bind(tag=TAG).info("Stopped listening.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def speech_to_text(audio):
    choose_asr=config['choose']['asr']
    if choose_asr=='asr_baidu':
        return speech_to_text_baidu(audio)
    elif choose_asr=="asr_paraformer":
        result=speech_to_text_paraformer(
            audio_file_path=audio,
            api_key=config['asr']['asr_paraformer']['dashscope.api_key'],
            language_hints=config['asr']['asr_paraformer']['language_hints']
        )
        return result
    else:
        logger.bind(tag=TAG).warning("No ASR selected.")
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


def audio_to_text(timeout=5):
    """带超时的语音转文字"""
    if(is_tts_working()):
        set_recording_requested(True)
        return None
    set_recording_requested(False)
    audio_file = record_audio_until_silence(timeout=timeout)
    if not audio_file:
        return None

    text = speech_to_text(audio_file)
    if text:
        logger.bind(tag=TAG).info("Recognized text:", text)
        return text
    else:
        logger.bind(tag=TAG).warning("Could not convert audio to text.")
        return None

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

