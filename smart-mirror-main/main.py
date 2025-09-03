import time
from features.common.config_loader import config
from flask import Flask, render_template
import geocoder
from features.llm.qwen import LLM
from features.face_recognition.face_recognition_system import FaceRecognition
from features.common.utils import audio_to_text, load_known_faces_from_folder
from features.weather import WeatherService
from queue import Queue
from features.common.globals import set_tts_state, is_tts_working
from features.tts.tts_speech import tts_speech
from log.load_log import logger
import uvicorn
import threading



TAG = __name__
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
llm=LLM()
running = True
face_detected = False
face_detection_active = False
preloaded_face_data = None
location_info = None
weather_service = WeatherService()
assistant = None
face_detection_running = False
ignore_audio_until = False
face_detection_success = False
detection_mode = None
human_detector = None
voice_detection_active = True
cali=False
# 全局线程锁
global_lock = threading.Lock()

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

    detection_thread = threading.Thread(target=recognition_wrapper)
    detection_thread.start()
    detection_thread.join(timeout=timeout)

    if not result_queue.empty():
        result = result_queue.get()
        if result:  # 只有识别成功才返回True
            logger.bind(tag=TAG).info(f"Face recognized: {result}")
            return True

    logger.bind(tag=TAG).info("Face recognition failed or timed out")
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
    # 助手模式
    global face_detected, running,cali
    listening_duration = 600
    last_interaction = time.time()

    # 移除了初始问候语，因为在人脸识别成功后已经播放
    while running and face_detected:
        if is_tts_working():
            time.sleep(0.1)
            last_interaction = time.time()
            continue



        if float(time.time()) - last_interaction > listening_duration:
            tts_speech("等待唤醒...")
            with global_lock:
                face_detected = False
            break

        try:
            text = audio_to_text(timeout=30)
            if text:
                logger.bind(tag=TAG).info(f"User said: {text}")
                last_interaction = time.time()
                set_tts_state(True)

                if len(text)<20 and ('拜拜' in text or '再见' in text or "bye" in text):
                    tts_speech("拜拜，下次再见！")
                    with global_lock:
                        face_detected = False
                elif '关闭系统' in text:
                    tts_speech("好的，正在关闭系统。")
                    with global_lock:
                        running = False
                else:
                    response = llm.chat(text)
                    tts_speech(response)
        except Exception as e:
            logger.bind(tag=TAG).error(f"语音识别错误: {e}")
            set_tts_state(False)
            time.sleep(0.1)


def on_human_detected():
    global ignore_audio_until, face_detected, face_detection_running

    if face_detection_running or face_detected:
        return

    logger.bind(tag=TAG).info("[人体检测] 红外感应触发")
    ignore_audio_until = time.time() + 3
    tts_speech("检测到您靠近，请面向摄像头。")
    threading.Thread(target=run_face_detection, args=("pir",)).start()


def run_face_detection(mode):
    global face_detection_running, face_detection_success, detection_mode
    global human_detector, voice_detection_active, face_detected

    human_detect_bool = config.get("human_detection", False)
    if not human_detect_bool:
        face_detected=True
        threading.Thread(target=assistant_mode).start()
    else:
        try:
            if face_detection_running or face_detected:
                return

            face_detection_running = True
            detection_mode = mode

            if mode == "pir":
                voice_detection_active = False
            elif mode == "voice":
                human_detector.stop_detection()

            logger.bind(tag=TAG).info(f"[人脸识别] 开始检测 (模式: {mode})")

            # 真正进行人脸识别，不再直接设置成功
            if detect_face(timeout=60):
                logger.bind(tag=TAG).info("人脸识别成功")
                with global_lock:
                    face_detected = True
                threading.Thread(target=assistant_mode).start()
            else:
                tts_speech("我无法识别您的面部。如果需要我，请随时叫我。")
                # 人脸识别失败后重新启用对应检测
                if mode == "pir":
                    human_detector.start_detection(on_human_detected)
                elif mode == "voice":
                    voice_detection_active = True

        except Exception as e:
            logger.bind(tag=TAG).error(f"[人脸识别] 异常: {e}")
            # 异常情况下也重新启用检测
            if mode == "pir":
                human_detector.start_detection(on_human_detected)
            elif mode == "voice":
                voice_detection_active = True
        finally:
            face_detection_running = False
            # 无论成功与否，都重新启用检测机制
            if mode == "pir":
                voice_detection_active = True
            elif mode == "voice":
                human_detector.start_detection(on_human_detected)


def wake_word_detection_loop():
    global running, face_detected, voice_detection_active

    while True:
        with global_lock:
            if not running:
                break
            if face_detected or not voice_detection_active:
                time.sleep(0.5)
                continue
        if is_tts_working():
            time.sleep(0.5)
            continue

        try:
            script = audio_to_text(timeout=30)
            if script:
                logger.bind(tag=TAG).info(f"检测到语音: {script}")
                for wake_word in config['wakeup_words']:
                    if wake_word in script:
                        with global_lock:
                            set_tts_state(True)
                            tts_speech("唤醒成功，请面向摄像头。")
                        threading.Thread(target=run_face_detection, args=("voice",)).start()
                        break
        except Exception as e:
            logger.bind(tag=TAG).warning(f"处理唤醒词出错: {e}")
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
    global running, assistant, preloaded_face_data, human_detector
    logger.bind(tag=TAG).info("Starting Smart Mirror...")

    try:
        # 预加载人脸数据
        preloaded_face_data = preload_face_data()
        logger.bind(tag=TAG).info("人脸数据预加载完成")

        # 初始化并启动人体检测模块
        human_detect_bool = config.get('human_detection', False)
        if human_detect_bool:
            from human_detection import HumanDetection  # 导入人体检测模块
            logger.bind(tag=TAG).info("已启用人体检测")
            human_detector = HumanDetection()
            human_detector.start_detection(on_human_detected)
        else:
            logger.bind(tag=TAG).info("已禁用人体检测")
        # human_detector = HumanDetection()
        # human_detector.start_detection(on_human_detected)

        # 启动GUI界面
        gui_thread = threading.Thread(target=launch_gui)
        gui_thread.daemon = True
        gui_thread.start()

        # 启动唤醒词检测
        voice_thread = threading.Thread(target=wake_word_detection_loop)
        voice_thread.daemon = True
        voice_thread.start()

        logger.bind(tag=TAG).info("系统启动完成，等待唤醒...")

        # 主循环
        while running:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.bind(tag=TAG).info("正在释放资源，请耐心等待...")
        with global_lock:
            running = False
        # 清理人体检测资源
        if human_detector:
            human_detector.stop_detection()
            human_detector.cleanup()
        logger.bind(tag=TAG).info("程序已终止")
    except Exception as e:
        logger.bind(tag=TAG).error(f"程序异常: {e}")


if __name__ == "__main__":
    main()
