import os
import yaml
from features.common.config_loader import config as _global_config

class ContextManager:
    ##
    # 上下文管理、大模型记忆
    # #
    def __init__(self, user_id):
        self.user_id = user_id
        self.config = _global_config
        self.context = self._load_role()

    def _load_role(self):
        # 加载角色设定
        role = self.config['context_manager']['role']
        context = [{"role": "system", "content": role}]
        return context

    def add_user_context(self, text):
        # 添加用户输入的文本到上下文
        self.context.append({"role": "user", "content": text})

    def add_assistant_context(self, text):
        # 添加助手的回复到上下文
        self.context.append({"role": "assistant", "content": text})

    def context_manager(self):
        pass

    def save_context(self):
        # 存储上下文到磁盘

        pass

    def load_context(self):
        # 从磁盘中加载上下文
        pass


