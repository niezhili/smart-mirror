import time
import RPi.GPIO as GPIO
import threading


class HumanDetection:
    def __init__(self, pin=17, timeout=15, interval=0.1, consecutive_detections_required=2):
        self.pin = pin
        self.timeout = timeout
        self.interval = interval
        self.consecutive_detections_required = consecutive_detections_required
        self.running = False
        self.detection_thread = None
        self.callback = None
        self.last_motion_time = 0
        self.consecutive_detections = 0
        self.person_present = False
        self.active_until = 0
        self.last_trigger_time = 0
        self.trigger_cooldown = 10

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def _check_presence(self):
        current_time = time.time()
        motion_detected = GPIO.input(self.pin) == 1

        if motion_detected:
            self.last_motion_time = current_time
            self.consecutive_detections += 1

            if self.consecutive_detections >= self.consecutive_detections_required:
                if not self.person_present:
                    self.person_present = True
                    self.active_until = current_time + self.timeout
                    if current_time - self.last_trigger_time > self.trigger_cooldown:
                        self.last_trigger_time = current_time
                        return True
        else:
            self.consecutive_detections = 0

        if self.person_present and current_time < self.active_until:
            return False

        if (self.person_present and
                (current_time - self.last_motion_time > self.timeout) and
                current_time > self.active_until):
            self.person_present = False
            return False

        return False

    def start_detection(self, callback=None):
        if self.running:
            return

        self.callback = callback
        self.running = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()

    def _detection_loop(self):
        print("[人体检测] 线程已启动")

        try:
            while self.running:
                if self._check_presence():
                    print("[人体检测] 检测到人体靠近！")
                    if self.callback:
                        self.callback()
                    time.sleep(2)

                time.sleep(self.interval)
        except Exception as e:
            print(f"[人体检测] 异常: {e}")
        finally:
            print("[人体检测] 线程已停止")

    def stop_detection(self):
        self.running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=1)

    def cleanup(self):
        self.stop_detection()
        GPIO.cleanup()