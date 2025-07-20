import os
import yaml

class ContextManager:
    ##
    # 上下文管理、大模型记忆
    # #
    def __init__(self, user_id):
        self.user_id = user_id
        self.config = self._load_config()
        self.context = self._load_role()

    def _load_config(self):
        # 加载配置文件，返回yaml对象
        config_path = os.path.join(os.path.dirname(__file__), "../../config/config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

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


