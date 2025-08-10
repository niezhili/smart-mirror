from features.llm.context_manager import ContextManager
from features.common.log_loader import logger
from dashscope import Generation
from features.common.config_loader import config
from features.common.text_clean import text_clean

TAG =__name__
_default_context_manager = None
def chat_llm(text="",context_manager:ContextManager = None)->None or str:
    global _default_context_manager
    # 如果没有传入对象，创建一个默认的ContextManager对象
    if context_manager is None:
        if _default_context_manager is None:
            logger.bind(tag=TAG).info("========未传入上下文对象，使用默认用户=========")
            _default_context_manager=ContextManager(user_id="default")
        context_manager=_default_context_manager
    # 文本清洗
    cleaned_text=text_clean(text)
    if cleaned_text=="":
        logger.bind(tag=TAG).warning("清洗后文本为空")
        return None
    # 添加用户输入
    context_manager.add_user_context(cleaned_text)
    context=context_manager.context
    # 调用模型
    which_llm=config['choose']['llm']
    if which_llm=="qwen":
        assistant_context=qwen_chat(context)
        if assistant_context =="":
            return None
        else:
            context_manager.add_assistant_context(assistant_context)
            return assistant_context
    elif which_llm=="deepseek":
        assistant_context=deepseek_chat(context)
        if assistant_context =="":
            return None
        else:
            context_manager.add_assistant_context(assistant_context)
            return assistant_context
    else:
        logger.bind(tag=TAG).warning("请检查yaml配置，暂不支持当前llm选项")
        return None


def deepseek_chat(messages):
    pass

def qwen_chat(context:list,temperature=0.7,top_p=0.9)->str:
    try:
        response = Generation.call(
            api_key=config['llm']['qwen']['qwen_api_key'],
            model=config['llm']['qwen']['model'],
            messages=context,
            result_format="message",
            temperature=temperature,
            top_p=top_p
        )
        if response and response.output and response.output.choices:
            logger.bind(tag=TAG).info(f"模型返回：{response.output.choices[0].message.content}")
            return response.output.choices[0].message.content
        else:
            logger.bind(tag=TAG).warning("模型返回为空。")
            return ""
    except Exception as e:
        logger.bind(tag=TAG).error(f"模型调用错误：{e}")
        return ""
