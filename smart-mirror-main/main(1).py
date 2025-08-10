import os
import sys
from flask import Flask, render_template
import geocoder
from features.face_recognition.face_recognition_system import FaceRecognition
from features.common.utils import read_text_baidu, user_speech_recognition, record_audio_until_silence, audio_to_text, \
    text_to_speech_chinese, load_known_faces_from_folder
from features.voice_feat_system import VoiceAssistant
from features.weather import WeatherService
import time
import threading
import signal
from human_detection import HumanDetection
import sounddevice as sd

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# 全局状态变量
running = True
face_detected = False
wake_words = ["小", "小朋友", "朋友",'你好','树莓派']
assistant = None
face_detection_running = False
face_detection_success = False
ignore_audio_until = 0
detection_mode = None
preloaded_face_data = None
human_detector = None
voice_detection_active = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test')
def test():
    return "Flask server is working!"


def check_audio_service():
    try:
        sd.check_input_settings()
        return True
    except:
        return False


def preload_face_data():
    global preloaded_face_data
    face_system = FaceRecognition()
    image_paths_by_person = load_known_faces_from_folder("known_faces")
    for person_name, image_paths in image_paths_by_person.items():
        face_system.add_new_person(person_name, image_paths)
    preloaded_face_data = face_system


def detect_face(timeout=60) -> bool:
    global preloaded_face_data, face_detection_running, detection_mode
    if preloaded_face_data is None:
        print("Error: Face data not preloaded.")
        return False

    start_time = time.time()
    print(f"[人脸识别] 开始 (触发方式: {detection_mode})")

    while time.time() - start_time < timeout and running:
        try:
            recognized = preloaded_face_data.start_recognition()
            if recognized:
                print("[人脸识别] 检测成功!")
                return True
            time.sleep(0.5)
        except Exception as e:
            print(f"[人脸识别] 出错: {e}")
            time.sleep(0.5)

    print(f"[人脸识别] 超时 ({timeout}秒)")
    return False


def run_face_detection(mode):
    global face_detection_running, face_detection_success, detection_mode
    global human_detector, voice_detection_active

    try:
        if face_detection_running or face_detected:
            return

        face_detection_running = True
        detection_mode = mode

        if mode == "pir":
            voice_detection_active = False
        elif mode == "voice":
            human_detector.stop_detection()

        print(f"[人脸识别] 开始检测 (模式: {mode})")

        if detect_face(timeout=60):
            face_detection_success = True
        else:
            read_text_baidu("我无法识别您的面部。如果需要我，请随时叫我。")

    except Exception as e:
        print(f"[人脸识别] 异常: {e}")
    finally:
        face_detection_running = False
        if mode == "pir":
            voice_detection_active = True
        elif mode == "voice":
            human_detector.start_detection(on_human_detected)


def on_human_detected():
    global ignore_audio_until

    if face_detection_running or face_detected:
        return

    print("[人体检测] 触发人脸识别")
    ignore_audio_until = time.time() + 3
    read_text_baidu("检测到您靠近，请面向摄像头。")
    threading.Thread(target=run_face_detection, args=("pir",)).start()


def wake_word_detection_loop():
    global running, face_detected, voice_detection_active
    global face_detection_success, ignore_audio_until

    no_wake_word_counter = 0
    NO_WAKE_WORD_PRINT_INTERVAL = 5

    while running:
        if not voice_detection_active or face_detected:
            time.sleep(1)
            continue

        if face_detection_success:
            face_detected = True
            face_detection_success = False
            threading.Thread(target=assistant_mode).start()
            continue

        if time.time() < ignore_audio_until:
            time.sleep(0.5)
            continue

        try:
            no_wake_word_counter += 1
            if no_wake_word_counter >= NO_WAKE_WORD_PRINT_INTERVAL:
                print("[语音检测] 正在监听唤醒词...")
                no_wake_word_counter = 0

            script = user_speech_recognition()
            if script:
                for wake_word in wake_words:
                    if wake_word in script:
                        print(f"[语音检测] 检测到唤醒词: {wake_word}")
                        ignore_audio_until = time.time() + 3
                        read_text_baidu("唤醒成功，请面向摄像头。")

                        face_thread = threading.Thread(target=run_face_detection, args=("voice",))
                        face_thread.start()
                        face_thread.join(timeout=60)

                        if not face_detection_success:
                            voice_detection_active = True
                            print("[语音检测] 人脸识别失败，恢复语音检测")
                        break
        except Exception as e:
            print(f"[语音检测] 异常: {e}")
            voice_detection_active = True
            time.sleep(5)

        time.sleep(1)


def assistant_mode():
    global running, face_detected, assistant, ignore_audio_until
    global human_detector, voice_detection_active

    if assistant is None:
        print("错误: 语音助手未初始化.")
        return

    print("[助手模式] 已激活")
    ignore_audio_until = time.time() + 5
    read_text_baidu("你好！有什么我可以帮您？")

    human_detector.stop_detection()
    voice_detection_active = False

    try:
        while running and face_detected:
            if time.time() < ignore_audio_until:
                time.sleep(0.5)
                continue

            text = user_speech_recognition()
            if text:
                print(f"用户说: {text}")

                if '天气' in text:
                    handle_weather_query()
                elif '几点' in text:
                    handle_time_query()
                elif '空调' in text:
                    handle_ac_control()
                elif '拜拜' in text or '再见' in text:
                    handle_goodbye()
                else:
                    handle_general_query(text)
            else:
                print("正在监听命令...")
                time.sleep(1)
    finally:
        face_detected = False
        human_detector.start_detection(on_human_detected)
        voice_detection_active = True
        print("[助手模式] 已退出，恢复检测功能")


def handle_weather_query():
    global ignore_audio_until
    location = get_user_location()
    weather = WeatherService()
    response = weather.get_weather_info(location.lng, location.lat)

    print("检测到天气查询")
    ignore_audio_until = time.time() + 30
    read_text_baidu(f"今天的天气状况如下, 位置:{location.city}")
    read_text_baidu(f"天气：{response['weather_condition']}")
    read_text_baidu(f"温度：{response['temperature']}")
    read_text_baidu(f"体感温度：{response['feels_like']}")
    read_text_baidu(f"湿度：{response['humidity']}")
    read_text_baidu(f"风向：{response['wind_direction']}")
    read_text_baidu(f"风速：{response['wind_speed']}")
    read_text_baidu(f"气压：{response['pressure']}")
    read_text_baidu(f"能见度：{response['visibility']}")
    read_text_baidu(f"云量：{response['cloud_coverage']}")


def handle_time_query():
    global ignore_audio_until
    print("检测到时间查询")
    ignore_audio_until = time.time() + 5
    read_text_baidu(f"现在是 {time.strftime('%H:%M')}")


def handle_ac_control():
    global ignore_audio_until
    print("检测到空调控制")
    ignore_audio_until = time.time() + 5
    read_text_baidu("好的，正在处理空调指令。")


def handle_goodbye():
    global face_detected
    read_text_baidu("拜拜，下次再见！")
    face_detected = False


def handle_general_query(text):
    global ignore_audio_until
    print(f"Deepseek请求: {text}")
    ignore_audio_until = time.time() + 10
    response = assistant.chat(text)
    print(f"DeepSeek响应: {response}")
    read_text_baidu(response)


def get_user_location():
    try:
        return geocoder.ip("me")
    except Exception as e:
        print(f"获取位置时出错: {e}")
        return None


def signal_handler(sig, frame):
    global running, human_detector
    print("\n正在关闭程序...")
    running = False
    human_detector.cleanup()
    time.sleep(1)
    os._exit(0)


def main():
    global running, assistant, preloaded_face_data, human_detector

    print("智能镜子系统启动中...")
    signal.signal(signal.SIGINT, signal_handler)

    if not check_audio_service():
        print("[警告] 音频服务不可用，将禁用语音功能")
        global voice_detection_active
        voice_detection_active = False
    else:
        print("[音频] 服务检查正常")

    assistant = VoiceAssistant(
        baidu_app_id=os.getenv("BAIDU_APP_ID"),
        baidu_api_key=os.getenv("BAIDU_API_KEY"),
        baidu_secret_key=os.getenv("BAIDU_SECRET_KEY"),
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY"),
    )

    preload_face_data()

    human_detector = HumanDetection()
    human_detector.start_detection(on_human_detected)

    voice_thread = threading.Thread(target=wake_word_detection_loop, daemon=True)
    voice_thread.start()

    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"Flask服务器错误: {e}")
    finally:
        running = False
        human_detector.cleanup()


if __name__ == "__main__":
    main()