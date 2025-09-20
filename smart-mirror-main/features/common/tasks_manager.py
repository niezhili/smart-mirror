import asyncio
from typing import List, Callable, Any, Dict, Optional
from features.common.log_loader import logger
import uuid
TAG=__name__

class TaskGroup:
    # 任务组
    group_id:str
    items:List[Any]
    cancel_event:asyncio.Event

    def __init__(self, items: List[Any]):
        # uuid任务标识符
        self.group_id = str(uuid.uuid4())[:8]
        self.items = items
        self.cancel_event = asyncio.Event()

    def cancel(self):
        logger.bind(tag=TAG).debug(f"任务组 {self.group_id} 被取消")
        self.cancel_event.set()

    async def is_cancelled(self):
        return self.cancel_event.is_set()

class TasksManager:
    # 任务管理器
    def __init__(self, worker: Callable[[Any], Any], max_concurrent_items: int = 3,waiting:bool = True):
        self.worker = worker
        self.max_concurrent_items = max_concurrent_items

        # 队列存放任务组
        self.queue: asyncio.Queue[TaskGroup] = asyncio.Queue()
        self.task_groups: Dict[str, TaskGroup] = {}
        self.lock = asyncio.Lock()


        # 启动消费者协程
        self.consumer_task = asyncio.create_task(self._consumer())
        self.waiting = waiting

    async def add_group(self, items: List[Any]) -> Optional[str]:
        """添加一个任务块，返回 group_id"""
        if not items:
            return None

        group = TaskGroup(items)
        await self.queue.put(group)

        async with self.lock:
            self.task_groups[group.group_id] = group

        # logger.bind(tag=TAG).info(f"[添加] 添加任务组 {group.group_id}，包含 {len(items)} 个任务")
        return group.group_id

    async def cancel_group(self, group_id: str):
        """取消一个任务组"""
        async with self.lock:
            group = self.task_groups.get(group_id)
            if group:
                group.cancel()
            else:
                logger.bind(tag=TAG).debug(f"[取消] 任务组 {group_id} 不存在或已完成")

    async def _consumer(self):
        """消费者：从队列中取出任务组，逐个处理任务"""
        while True:
            try:
                group = await self.queue.get()
            except asyncio.CancelledError:
                # logger.bind(tag=TAG).debug("[消费者] 被取消")
                break

            task = asyncio.create_task(self._process_group(group))
            if self.waiting:
                await task
            # 可以选择等待 task，或让它后台运行（推荐）
            # 这里我们让它后台运行，避免阻塞下一个 group
            # 你也可以 await task，表示顺序处理每个 group

    async def _process_group(self, group: TaskGroup):
        """处理单个任务组"""
        try:
            # logger.bind(tag=TAG).info(f"[开始] 处理任务组 {group.group_id}")

            semaphore = asyncio.Semaphore(self.max_concurrent_items)
            tasks = []

            for item in group.items:
                async def wrapped_task(i=item):
                    # 检查是否已取消
                    if await group.is_cancelled():
                        logger.bind(tag=TAG).debug(f"跳过任务: {i}（所属组已取消）")
                        return

                    async with semaphore:
                        # 再次检查（防止在等待信号量时被取消）
                        if await group.is_cancelled():
                            logger.bind(tag=TAG).debug(f"跳过任务: {i}（等待信号量时被取消）")
                            return

                        # 执行实际任务
                        try:
                            await self.worker(i)
                        except Exception as e:
                            logger.bind(tag=TAG).error(f"任务 {i} 执行出错: {e}")

                task = asyncio.create_task(wrapped_task())
                tasks.append(task)

            # 等待所有任务完成（包括被跳过的）
            await asyncio.gather(*tasks, return_exceptions=True)
            # logger.bind(tag=TAG).success(f"[完成] 任务组 {group.group_id} 处理完毕")

        except Exception as e:
            logger.bind(tag=TAG).error(f"处理任务组 {group.group_id} 时发生错误: {e}")
        finally:
            # 无论成功或失败，都从管理字典中移除
            async with self.lock:
                self.task_groups.pop(group.group_id, None)
            self.queue.task_done()
