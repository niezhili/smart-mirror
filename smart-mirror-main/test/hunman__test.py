import time
import threading
from human_detection import HumanDetection


def test_human_detection():
    """
    测试 HumanDetection 类的功能
    """
    print("开始测试人体检测功能...")

    # 模拟运动检测的变量
    motion_simulated = False
    motion_toggle_time = time.time()

    def simulate_motion():
        """
        模拟人体运动检测的辅助函数
        """
        nonlocal motion_simulated, motion_toggle_time
        current_time = time.time()

        # 每3秒切换一次运动状态，模拟有人经过
        if current_time - motion_toggle_time > 3:
            motion_simulated = not motion_simulated
            motion_toggle_time = current_time
            print(f"[模拟] 运动检测: {'检测到运动' if motion_simulated else '无运动'}")

        return motion_simulated

    def on_human_detected_callback():
        """
        人体检测回调函数
        """
        print("[测试] >>> 人体检测回调被触发！<<<")
        print("[测试] 人体检测功能正常工作")

    # 创建 HumanDetection 实例（使用默认参数）
    detector = HumanDetection(
        pin=17,  # GPIO引脚（虽然当前未使用）
        timeout=5,  # 缩短超时时间便于测试
        interval=0.1,
        consecutive_detections_required=2,
        trigger_cooldown=3  # 缩短冷却时间便于测试
    )

    # 修改 _check_presence 方法以使用模拟的运动检测
    def mock_check_presence():
        return detector._check_presence(simulate_motion())

    # 替换原方法
    detector._check_presence = mock_check_presence

    print("启动人体检测...")
    detector.start_detection(on_human_detected_callback)

    print("测试将在15秒后自动停止...")
    test_start_time = time.time()

    try:
        # 运行测试15秒
        while time.time() - test_start_time < 15:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    finally:
        print("停止人体检测...")
        detector.cleanup()
        print("测试结束")


def test_human_detection_manual():
    """
    手动测试版本 - 你可以手动触发运动检测
    """
    print("开始手动测试人体检测功能...")
    print("输入 'm' 模拟检测到运动，输入 'q' 退出测试")

    motion_detected = False

    def on_human_detected_callback():
        print("[测试] >>> 人体检测回调被触发！<<<")

    # 创建检测器实例
    detector = HumanDetection(
        timeout=5,
        interval=0.1,
        consecutive_detections_required=2,
        trigger_cooldown=3
    )

    # 修改检测方法以使用手动控制的运动状态
    def manual_check_presence():
        return detector._check_presence(motion_detected)

    detector._check_presence = manual_check_presence

    # 启动检测
    detector.start_detection(on_human_detected_callback)

    try:
        while True:
            user_input = input().strip().lower()
            if user_input == 'm':
                motion_detected = not motion_detected
                print(f"[手动] 运动检测状态: {'检测到运动' if motion_detected else '无运动'}")
            elif user_input == 'q':
                break
            else:
                print("输入 'm' 切换运动状态，输入 'q' 退出")
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    finally:
        detector.cleanup()
        print("手动测试结束")


if __name__ == "__main__":
    print("请选择测试模式:")
    print("1. 自动模拟测试")
    print("2. 手动测试")

    choice = input("请输入选择 (1 或 2): ").strip()

    if choice == "1":
        test_human_detection()
    elif choice == "2":
        test_human_detection_manual()
    else:
        print("无效选择，运行自动测试")
        test_human_detection()
