import os
import time
import yaml
import threading
from flask import Flask, render_template
import geocoder
from loguru import logger
from features.face_recognition.face_recognition_system import FaceRecognition
from features.common.utils import tts_speech, user_speech_recognition, audio_to_text, load_known_faces_from_folder
from features.voice_feat_system import VoiceAssistant
from features.weather import WeatherService
from queue import Queue
from features.common.globals import set_tts_state, is_recording_requested, is_tts_working, set_recording_requested

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config/config.yaml")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    Config = yaml.safe_load(f)
config=Config
TAG = __name__

# Initialize Flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Global flags and variables
running = True
face_detected = False
face_detection_active = False  # Replaces multiple flags
preloaded_face_data = None
location_info = None  # Cache location info
weather_service = WeatherService()
assistant = None

WAKE_WORD_CHECK_INTERVAL = 0.1  # 唤醒词检查间隔
FACE_DETECT_TIMEOUT = 30  # 人脸检查超时

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return "Flask server is working!"


def preload_face_data():
    face_system = FaceRecognition()
    image_paths_by_person = load_known_faces_from_folder("known_faces")
    for person_name, image_paths in image_paths_by_person.items():
        face_system.add_new_person(person_name, image_paths)
    return face_system

def detect_face(timeout=FACE_DETECT_TIMEOUT) -> bool:
    global preloaded_face_data
    if preloaded_face_data is None:
        logger.bind(tag=TAG).error("Face data not preloaded.")
        return False
    result_queue = Queue()
    def recognition_wrapper():
        result = preloaded_face_data.start_recognition()
        result_queue.put(result)



    start_time = time.time()
    detection_thread = threading.Thread(target=preloaded_face_data.start_recognition)
    detection_thread.start()

    # Wait for result with timeout
    while time.time() - start_time < timeout and detection_thread.is_alive():
        if not result_queue.empty():
            result = result_queue.get()
            logger.bind(tag=TAG).info(f"Face detected: {result}")
            return True
        time.sleep(0.1)

    return False


def get_user_location():
    global location_info
    if location_info is None:
        try:
            location_info = geocoder.ip("me")
        except Exception as e:
            logger.bind(tag=TAG).error(f"Error getting location: {e}")
            return None
    return location_info


def play_weather_info():
    location = get_user_location()
    if not location:
        tts_speech("无法获取位置信息")
        return

    try:
        weather_info = weather_service.get_weather_info(location.lng, location.lat)
        # Single TTS call with combined information
        message = (
            f"今天的天气状况如下，位置：{location.city}。"
            f"天气：{weather_info['weather_condition']}，"
            f"温度：{weather_info['temperature']}，"
            f"体感温度：{weather_info['feels_like']}，"
            f"湿度：{weather_info['humidity']}，"
            f"风向：{weather_info['wind_direction']}，"
            f"风速：{weather_info['wind_speed']}，"
            f"气压：{weather_info['pressure']}，"
            f"能见度：{weather_info['visibility']}，"
            f"云量：{weather_info['cloud_coverage']}"
        )
        tts_speech(message)
    except Exception as e:
        logger.bind(tag=TAG).error(f"Weather playback error: {e}")


def assistant_mode():
    global face_detected, assistant
    if assistant is None:
        logger.bind(tag=TAG).error("Assistant not initialized.")
        return

    listening_duration = 60
    last_interaction = time.time()
    tts_speech("你好！有什么我可以帮您？")

    while running and face_detected:
        if time.time() - last_interaction > listening_duration:
            tts_speech("等待唤醒...")
            face_detected = False
            break

        try:
            text = user_speech_recognition(timeout=5)  # Add timeout to non-blocking
            if text:
                logger.bind(tag=TAG).info(f"User said: {text}")
                last_interaction = time.time()

                if '天气' in text:
                    threading.Thread(target=play_weather_info).start()
                elif '几点' in text:
                    tts_speech(f"现在是 {time.strftime('%点%M分')}")
                elif '空调' in text:
                    tts_speech("好的，正在处理空调指令。")
                elif '拜拜' in text or '再见' in text:
                    tts_speech("拜拜，下次再见！")
                    face_detected = False
                else:
                    response = assistant.chat(text)
                    threading.Thread(target=tts_speech, args=(response,)).start()
        except Exception as e:
            logger.bind(tag=TAG).error(f"Speech recognition error: {e}")
            time.sleep(WAKE_WORD_CHECK_INTERVAL)

def wake_word_detection_loop():
    global running, face_detected

    while running:
        if face_detected:
            time.sleep(0.5)
            continue

        try:
            script = audio_to_text(timeout=5)  # Original function doesn't support timeout
            if script:
                for wake_word in ["你好", "树莓派", "小", "小朋友", "朋友"]:
                    if wake_word in script:
                        logger.bind(tag=TAG).info("Wake word detected")
                        set_tts_state(True)
                        tts_speech("唤醒成功，请扫描您的面部以便继续互动")
                        set_tts_state(False)
                        # if detect_face():
                        face_detected = True
                        threading.Thread(target=assistant_mode).start()
                        break
                        # else:
                        #     tts_speech("未检测到您的面部，请重新尝试")
            else:
                logger.bind(tag=TAG).debug("No speech detected")

        except Exception as e:
            logger.bind(tag=TAG).warning(f"Error processing wake word: {e}")

        time.sleep(0.1)


def launch_gui():
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QUrl
        import sys

        app = QApplication(sys.argv)
        web = QWebEngineView()
        web.load(QUrl("http://localhost:8080"))
        web.show()
        sys.exit(app.exec_())
    except ImportError:
        try:
            from kivy.app import App
            from kivy.uix.label import Label

            class SimpleApp(App):
                def build(self):
                    return Label(text='Display Error, your Smart Mirror is Running\nhttp://localhost:8080')

            SimpleApp().run()
        except ImportError:
            logger.bind(tag=TAG).warning("Running in console mode. GUI frameworks not available")


def main():
    global running, assistant, preloaded_face_data,config
    logger.bind(tag=TAG).info("Starting Smart Mirror...")

    # Initialize voice assistant
    assistant = VoiceAssistant(
        baidu_app_id=config['tts']['tts_baidu']['baidu_app_id'],
        baidu_api_key=config['tts']['tts_baidu']['baidu_api_key'],
        baidu_secret_key=config['tts']['tts_baidu']['baidu_secret_key'],
        deepseek_api_key=config['llm']['deepseek']['deepseek_api_key'],
    )

    # Preload face data
    preloaded_face_data = preload_face_data()

    # Start services
    gui_thread = threading.Thread(target=launch_gui)
    voice_thread = threading.Thread(target=wake_word_detection_loop, daemon=True)

    gui_thread.start()
    voice_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.bind(tag=TAG).info("Shutting down...")
        global running
        running = False
        voice_thread.join()


if __name__ == "__main__":
    main()
