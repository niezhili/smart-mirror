import RPi.GPIO as GPIO
import time
from features.common.log_loader import logger
TAG=__name__
GPIO.setmode(GPIO.BCM)
pin = 17
GPIO.setup(pin, GPIO.IN)

try:
    while True:
        logger.bind(tag=TAG).info(f"GPIO {pin} 输入值: {GPIO.input(pin)}")
        # print(f"GPIO {pin} 输入值: {GPIO.input(pin)}")
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()