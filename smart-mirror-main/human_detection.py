import time
import RPi.GPIO as GPIO
import threading
import logging

# 设置日志
logger = logging.getLogger(__name__)


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

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)
            logger.info("红外传感器初始化成功 (引脚: %s)", pin)
        except Exception as e:
            logger.error("红外传感器初始化失败: %s", e)
            # 即使初始化失败，也允许程序继续运行，但检测功能将不可用
            self.running = False

    def _check_presence(self):
        current_time = time.time()
        try:
            motion_detected = GPIO.input(self.pin) == 1
        except Exception as e:
            logger.error("读取传感器失败: %s", e)
            return False

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
            logger.warning("检测已在运行中")
            return

        self.callback = callback
        self.running = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        logger.info("人体检测已启动")

    def _detection_loop(self):
        logger.info("[人体检测] 线程已启动")

        try:
            while self.running:
                try:
                    if self._check_presence():
                        logger.info("[人体检测] 检测到人体靠近！")
                        if self.callback:
                            self.callback()
                        # 检测到人体后暂停检测，避免重复触发
                        time.sleep(self.timeout)
                except Exception as e:
                    logger.error("检测循环中出现异常: %s", e)

                time.sleep(self.interval)

        except Exception as e:
            logger.error("检测循环发生严重错误: %s", e)
        finally:
            logger.info("[人体检测] 线程已停止")

    def stop_detection(self):
        if not self.running:
            return

        logger.info("正在停止人体检测...")
        self.running = False

        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=1.0)
            if self.detection_thread.is_alive():
                logger.warning("人体检测线程未正常停止")

        logger.info("人体检测已停止")

    def cleanup(self):
        self.stop_detection()
        try:
            GPIO.cleanup()
            logger.info("GPIO资源已清理")
        except Exception as e:
            logger.warning("清理GPIO资源时出错: %s", e)


# 如果直接运行此文件，可用于测试
if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


    def test_callback():
        logger.info("人体检测回调被触发")


    logger.info("启动人体检测测试...")
    detector = HumanDetection()
    try:
        detector.start_detection(test_callback)
        logger.info("按 Ctrl+C 停止测试")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("停止测试...")
        detector.cleanup()