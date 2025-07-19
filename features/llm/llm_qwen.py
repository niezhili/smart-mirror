from loguru import logger
from dashscope import Generation
import yaml
import os

from features.common.utils import tts_speech

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config/config.yaml")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    Config = yaml.safe_load(f)
config=Config
TAG =__name__
def chat_llm(messages):
    global config
    which_llm=config['choose']['llm']
    if which_llm=="qwen":
        qwen_chat(messages)
    elif which_llm=="deepseek":
        deepseek_chat(messages)



def deepseek_chat(messages):
    pass



def qwen_chat(messages):
    response = Generation.call(
        api_key="sk-acccd325f0f7452b935947606d5b565a",
        model="qwen-turbo",
        messages=messages,
        result_format="message",
    )
    response = response.output.choices[0].message.content
    return response

