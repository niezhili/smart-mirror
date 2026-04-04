import asyncio
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass

@dataclass
class PlaybackJob:
    text_segments: List[str]        # 原始文本顺序
    received: Dict[str, str]        # 已收到的 {text: audio_path}
    started: bool                   # 是否已开始播放
    lock: asyncio.Lock

class StreamingOrderedPlayer:
    """
    可持续接收多批文本片段的有序播放器
    当某批的首个片段到达时，立即按顺序播放该批所有片段（已生成的）
    """

    def __init__(self, playback_callback: Callable[[str], None]):
        """
        :param playback_callback: 同步播放函数，如 play_audio(path)
        """
        self.playback_callback = playback_callback
        self.jobs: Dict[str, PlaybackJob] = {}  # job_id -> job
        self.job_lock = asyncio.Lock()
        self.global_event = asyncio.Event()
        self._task = asyncio.create_task(self._play_loop())
        self._closed = False

    async def submit_segment(self, text: str, audio_path: str, job_id: str):
        """
        提交一个文本片段的音频路径
        :param text: 文本内容（作为 key）
        :param audio_path: 音频文件路径
        :param job_id: 所属任务批次 ID（如 group_id）
        """
        if self._closed:
            return

        job: Optional[PlaybackJob] = None
        async with self.job_lock:
            if job_id not in self.jobs:
                # 如果还没有这个 job，先不创建，等待 add_job 显式添加
                print(f"[播放器] 警告: job_id {job_id} 不存在，无法提交片段 {text}")
                return  # 或抛警告
            job = self.jobs[job_id]
            job.received[text] = audio_path
            print(f"[播放器] 已提交片段: {text} -> {audio_path}，当前已收到 {len(job.received)}/{len(job.text_segments)} 段")

        # 触发播放检查
        self.global_event.set()

    async def add_job(self, job_id: str, text_segments: List[str]):
        """添加一个新的播放任务（文本列表）"""
        async with self.job_lock:
            self.jobs[job_id] = PlaybackJob(
                text_segments=text_segments.copy(),
                received={},
                started=False,
                lock=asyncio.Lock()
            )
        print(f"[播放器] 已注册播放任务: {job_id}, 共 {len(text_segments)} 段")

    async def _play_loop(self):
        while not self._closed:
            await self.global_event.wait()
            self.global_event.clear()

            # 检查所有未开始的任务，看是否可以启动
            jobs_to_check = []
            async with self.job_lock:
                jobs_to_check = [
                    (jid, job) for jid, job in self.jobs.items()
                    if not job.started
                ]

            for job_id, job in jobs_to_check:
                first_text = job.text_segments[0]
                if first_text in job.received:
                    # 第一个片段已到，启动播放
                    asyncio.create_task(self._play_job(job_id, job))

    async def _play_job(self, job_id: str, job: PlaybackJob):
        async with job.lock:
            job.started = True
        print(f"[播放器] 开始播放任务: {job_id}，共 {len(job.text_segments)} 段")

        for i, text in enumerate(job.text_segments):
            print(f"[播放器] 准备播放第 {i + 1} 段: {text}")
            # 等待该片段生成
            wait_count = 0
            while True:
                if self._closed:
                    print(f"[播放器] 播放器已关闭，停止播放任务: {job_id}，当前播放到第 {i + 1} 段")
                    return
                if text in job.received:
                    audio_path = job.received[text]
                    try:
                        print(f"[播放器] 播放第 {i + 1} 段: {text}")
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, self.playback_callback, audio_path)
                        print(f"[播放器] 完成播放第 {i + 1} 段: {text}")
                    except Exception as e:
                        print(f"[播放器] 播放失败 第 {i + 1} 段 {text}: {e}")
                    break
                # 等待新提交
                wait_count += 1
                if wait_count % 10 == 0:  # 每等待1秒打印一次
                    print(f"[播放器] 第 {i + 1} 段 {text} 尚未生成，已等待 {wait_count * 0.1} 秒...")
                await asyncio.sleep(0.1)

        # 播放完成后可选择清理
        async with self.job_lock:
            self.jobs.pop(job_id, None)
        print(f"[播放器] 播放完成: {job_id}，共播放 {len(job.text_segments)} 段")

    async def close(self):
        self._closed = True
        self.global_event.set()
        if self._task:
            await self._task

    async def wait_for_job_complete(self, job_id: str, timeout: float = 60.0):
        """等待指定任务播放完成"""
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            async with self.job_lock:
                if job_id not in self.jobs:
                    print(f"[播放器] 任务 {job_id} 已完成播放")
                    return True
            await asyncio.sleep(0.5)
        print(f"[播放器] 等待任务 {job_id} 完成超时")
        return False  # 超时

