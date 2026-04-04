import pyaudio
import numpy as np
import time
import threading


class VoiceActivityDetection:
    def __init__(self,
                 rate=16000,
                 chunk=1024,
                 channels=1,
                 format=pyaudio.paInt16,
                 threshold=500,
                 silence_duration=1.0):
        """
        初始化VAD检测器

        Args:
            rate: 采样率
            chunk: 音频块大小
            channels: 声道数
            format: 音频格式
            threshold: 能量阈值
            silence_duration: 静默持续时间阈值(秒)
        """
        self.rate = rate
        self.chunk = chunk
        self.channels = channels
        self.format = format
        self.threshold = threshold
        self.silence_duration = silence_duration

        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        self.vad_thread = None
        self.callback = None
        self.silence_start_time = None
        self.is_speaking = False

    def _calculate_energy(self, audio_data):
        """计算音频能量"""
        # 将字节数据转换为numpy数组
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        # 计算RMS能量
        energy = np.sqrt(np.mean(audio_np.astype(np.float32) ** 2))
        return energy

    def _vad_loop(self):
        """VAD检测循环"""
        print("[VAD] 开始检测")
        try:
            while self.running:
                # 读取音频数据
                data = self.stream.read(self.chunk, exception_on_overflow=False)

                # 计算音频能量
                energy = self._calculate_energy(data)

                # 判断是否有语音活动
                if energy > self.threshold:
                    # 检测到语音
                    current_time = time.time()
                    if not self.is_speaking:
                        self.is_speaking = True
                        self.silence_start_time = None
                        print(f"[VAD] 检测到语音活动，能量: {energy:.2f}")
                        if self.callback:
                            self.callback('speech_start')
                else:
                    # 未检测到语音
                    current_time = time.time()
                    if self.is_speaking:
                        if self.silence_start_time is None:
                            self.silence_start_time = current_time
                        elif current_time - self.silence_start_time >= self.silence_duration:
                            self.is_speaking = False
                            self.silence_start_time = None
                            print(f"[VAD] 检测到语音结束，能量: {energy:.2f}")
                            if self.callback:
                                self.callback('speech_end')
        except Exception as e:
            print(f"[VAD] 错误: {e}")
        finally:
            print("[VAD] 停止检测")

    def start_detection(self, callback=None):
        """
        开始VAD检测

        Args:
            callback: 回调函数，参数为事件类型('speech_start'或'speech_end')
        """
        if self.running:
            return

        self.callback = callback

        # 打开音频流
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        self.running = True
        self.vad_thread = threading.Thread(target=self._vad_loop, daemon=True)
        self.vad_thread.start()

    def stop_detection(self):
        """停止VAD检测"""
        self.running = False
        if self.vad_thread:
            self.vad_thread.join(timeout=1)

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def cleanup(self):
        """清理资源"""
        self.stop_detection()
        self.audio.terminate()

    def is_voice_active(self):
        """
        获取当前语音活动状态

        Returns:
            bool: True表示正在说话，False表示静默
        """
        return self.is_speaking


# 使用示例
if __name__ == "__main__":
    def vad_callback(event):
        if event == 'speech_start':
            print("=== 开始说话 ===")
        elif event == 'speech_end':
            print("=== 结束说话 ===")


    vad = VoiceActivityDetection(threshold=500)

    try:
        vad.start_detection(vad_callback)
        print("VAD检测已启动，按Ctrl+C停止...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止VAD检测...")
    finally:
        vad.cleanup()
