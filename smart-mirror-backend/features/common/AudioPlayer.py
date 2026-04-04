import os.path
import time
import pygame
from datetime import datetime
import uuid
from features.common.log_loader import logger
from features.common.text_cutter import text_cutter
from features.common.tasks_manager import TasksManager
from features.common.StreamingOrderedPlayer import StreamingOrderedPlayer
from features.tts.TTS import TtsManager
from features.tts.tts_huoshan import text_to_speech_huoshan_async
from path_hub import temp_tts_path_abs
from features.common.globals import set_tts_state
TAG = __name__


class AsyncAudioPlayer:
    def __init__(self):
        self._pygame_initialized = False
        self.channel = None
        self.tts=TtsManager()
        self.is_playing = False

    def _init_pygame_mixer(self):
        """初始化 pygame 音频系统（只初始化一次）"""
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            # 优化参数：减小 buffer 降低延迟
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self._pygame_initialized = True

        # 延迟初始化 channel，确保 mixer 已经初始化
        if self.channel is None:
            self.channel = pygame.mixer.Channel(0)

    def _seamless_play_audio(self, file_path: str, channel: pygame.mixer.Channel,
                             trim_end_seconds: float = 0.1, max_wait: float = 5.0):
        """
        无缝播放单个音频文件（支持排队）

        :param file_path: 音频文件路径
        :param channel: 使用的 mixer channel（建议固定一个用于顺序播放）
        :param trim_end_seconds: 裁剪末尾静音秒数（如 0.1 表示去掉最后 100ms）
        :param max_wait: 最大等待播放时间（防止卡死）
        """
        self._init_pygame_mixer()

        try:
            # 加载音频
            sound = pygame.mixer.Sound(file_path)
            total_length = sound.get_length()
            play_length = max(0.05, total_length - trim_end_seconds)

            logger.bind(tag=TAG).info(
                f"🎵 排队播放: {file_path} (总长: {total_length:.2f}s, 播放: {play_length:.2f}s)"
            )

            # 如果 channel 正在播放，queue 会自动排队
            channel.queue(sound)

            # 等待播放开始（可选：用于调试）
            start_time = time.time()
            while not channel.get_busy():
                if time.time() - start_time > 0.5:
                    break  # 等待最多 500ms 开始
                pygame.time.delay(10)

            # 等待播放结束（减去末尾）
            start_play = time.time()
            while channel.get_busy() and (time.time() - start_play < play_length):
                pygame.time.delay(10)

            # 强制 stop 以跳过末尾（可选）
            # channel.stop()  # 如果 queue 多个，不要 stop！

        except Exception as e:
            logger.bind(tag=TAG).error(f"❌ 播放失败 {file_path}: {e}")

    def _cleanup_pygame_mixer(self):
        """清理pygame mixer"""
        if self._pygame_initialized:
            try:
                pygame.mixer.quit()
                self._pygame_initialized = False
                self.channel = None  # 重置 channel
                logger.bind(tag=TAG).info("Pygame mixer 清理完成")
            except Exception as e:
                logger.bind(tag=TAG).error(f"Pygame mixer 清理失败: {str(e)}")

    async def _generate(self, text: str, player, job_id):
        """生成音频文件"""
        os.makedirs(temp_tts_path_abs, exist_ok=True)
        unique_id = str(uuid.uuid4())[:8]
        timestamps = datetime.now().strftime("%Y%m%d%H%M%S")
        audio_path = os.path.join(temp_tts_path_abs,f"tts_huoshan_{timestamps}_id{unique_id}.wav")
        # print(f"生成音频{audio_path}===============================================")
        language=self.tts._detect_language(text)
        await text_to_speech_huoshan_async(text=text, output_file=audio_path,language=language)
        if player:
            # 确保 player 有 submit_segment 方法
            if hasattr(player, 'submit_segment'):
                await player.submit_segment(text=text, audio_path=audio_path, job_id=job_id)
            else:
                print(f"ERROR: player 对象没有 submit_segment 方法: {type(player)}")
        else:
            logger.bind(tag=TAG).error("player 为 None")

        return text, audio_path

    def _sync_pygame_audio(self, file_paths, skip_last_frames: int = 0, use_seamless: bool = True):
        """
        同步播放音频文件
        :param file_paths: 单个路径或路径列表
        :param skip_last_frames: 要跳过的末尾秒数
        :param use_seamless: 是否启用无缝播放
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]

        if not file_paths:
            return

        trim_end_seconds = skip_last_frames

        # 初始化
        self._init_pygame_mixer()

        # 确保 channel 已初始化
        if self.channel is None:
            self.channel = pygame.mixer.Channel(0)

        for file_path in file_paths:
            if not use_seamless:
                # 保留你原来的逻辑（不推荐）
                sound = pygame.mixer.Sound(file_path)
                length = sound.get_length()
                play_length = max(0.1, length - trim_end_seconds)
                ch = sound.play()
                start = time.time()
                while time.time() - start < play_length and ch.get_busy():
                    pygame.time.delay(10)
                ch.stop()
            else:
                # 使用无缝播放
                self._seamless_play_audio(file_path, self.channel, trim_end_seconds=trim_end_seconds)

    async def speak(self, text: str, skip_last_frames: int = 0):
        try:# 1. 文本切分
            self.is_playing=True
            texts = self.tts.words_cut(text)
            logger.bind(tag=TAG).info(f"文本切分为 {len(texts)} 段: {texts}")

            # 2. 创建播放器实例
            player = StreamingOrderedPlayer(playback_callback=lambda file_path:
            self._sync_pygame_audio(file_path, skip_last_frames=skip_last_frames))

            # 3. 生成唯一任务ID
            job_id = str(uuid.uuid4())[:8]

            # 4. 添加任务到播放器
            await player.add_job(job_id, texts)

            # 5. 创建生成函数
            async def wrapped_generate(item):
                return await self._generate(item, player, job_id)

            # 6. 创建任务管理器
            task_manager = TasksManager(wrapped_generate, max_concurrent_items=4)

            # 7. 添加文本段到任务管理器
            await task_manager.add_group(texts)

            # 8. 等待所有TTS任务完成
            await task_manager.queue.join()

            # 9. 等待播放完成
            await player.wait_for_job_complete(job_id, timeout=300)
            # 10. 关闭播放器
            await player.close()

            logger.bind(tag=TAG).info(f"===================文本播放完成: {text}")
            return texts
        finally:
            self.is_playing=False
            set_tts_state(False)




    def cleanup(self):
        """清理资源"""
        self._cleanup_pygame_mixer()
