import os
import re
import emoji
import yaml
import json
def text_clean(text):
    ##
    # 文本清洗，过滤表情包、网址等
    # #
    text=emoji.replace_emoji(text, replace='')
    text = re.sub(r'(\*{1,2}|_)(.+?)(\*{1,2}|_)', r'\2', text)
    text = re.sub(r'!\[.*?]\(.*?\)', '', text)
    text = re.sub(r'$$(.+?)$$(?:$$.*?$$)?', r'\1', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[*-]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'https?://\S+', '', text)
    return text

class ContextManager:
    ##
    # 上下文管理、大模型记忆
    # #
    def __init__(self,user_id):
        self.user_id=user_id
        self.config=self._load_config()
        self.context= {}

    def _load_config(self):
        # 加载配置文件，返回对象
        config_path = os.path.join(os.path.dirname(__file__), "../../config/config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _init_role(self):
        return self.config['context_manager']['role']

    def _init_context(self):
        self.context={

        }
        pass

    def context_manager(self):
        pass

    def add_context(self,text):
        pass

    def save_context(self):
        # 存储上下文到磁盘
        pass

    def load_context(self):
        # 从磁盘中加载上下文
        pass


context={}
context['ww'] = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]
context[123] = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]
print(context)