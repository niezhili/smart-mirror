# 注意：此脚本需要使用专门的物联网Blinker库，而非通用的blinker信号库
# 正确的安装方法：
# git clone https://github.com/blinker-iot/blinker-pi.git
# cd blinker-pi
# python3 setup.py install

import time

try:
    from blinker import Blinker, BlinkerButton, BlinkerNumber
    BLINKER_LIBRARY_AVAILABLE = True
except ImportError:
    print("错误: 未找到正确的Blinker物联网库")
    print("请按照以下步骤安装正确的库：")
    print("1. git clone https://github.com/blinker-iot/blinker-pi.git")
    print("2. cd blinker-pi")
    print("3. python3 setup.py install")
    BLINKER_LIBRARY_AVAILABLE = False
    exit(1)

# 尝试初始化GPIO，仅在树莓派环境下可用
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
    # 初始化GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    LED_PIN = 18
    GPIO.setup(LED_PIN, GPIO.OUT)
    print("GPIO初始化成功")
except ImportError:
    GPIO_AVAILABLE = False
    print("警告: RPi.GPIO库不可用，GPIO控制功能将被禁用")

# 初始化Blinker
BLINKER_WIFI = False  # 禁用WiFi模式，使用局域网模式
blinker = Blinker("设备密钥")  # 替换为实际获取的设备密钥

# 配置局域网通信模式
blinker.setServer("树莓派IP地址", 8080)  # 设置树莓派IP和端口，需替换为实际IP

# 定义回调函数
def button_callback(state):
    """按钮控制回调函数"""
    print(f"按钮状态: {state}")
    # GPIO控制逻辑
    if GPIO_AVAILABLE:
        if state == 'on':
            GPIO.output(LED_PIN, GPIO.HIGH)  # 点亮GPIO18连接的LED
            print("LED已点亮")
        elif state == 'off':
            GPIO.output(LED_PIN, GPIO.LOW)   # 关闭LED
            print("LED已关闭")
    else:
        print(f"收到按钮控制指令: {state}，但GPIO功能不可用")

# 读取温度传感器数据示例
def read_temperature():
    """读取温度传感器数据示例"""
    # 实际项目中替换为真实传感器读取逻辑
    return 25.5

# 注册组件
btn1 = BlinkerButton("btn-abc")  # 按钮组件，需与APP端组件ID对应
btn1.attach(button_callback)

temp = BlinkerNumber("temp")  # 温度数值组件

# 主循环
if __name__ == '__main__':
    try:
        blinker.run()
        print("Blinker服务已启动，等待连接...")
        
        while True:
            # 每2秒上报一次温度数据
            temperature = read_temperature()
            temp.print(temperature)
            print(f"上报温度数据: {temperature}°C")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 仅在GPIO可用时清理资源
        if GPIO_AVAILABLE:
            GPIO.cleanup()
            print("GPIO资源已清理")