# # -*- coding: utf-8 -*-
# from features.common.tasks_manager import TasksManager
# from features.common.text_cutter import text_cutter
# from features.tts.TTS import TtsManager
# import os
# import time
#
# # tts=TtsManager()
# # words='''Hello，今天天气不错！我们一起去shopping吧？途中路过一家カフェ，里面播放着「Lemon」——这首歌是米津玄師的作品。It was raining yesterday; however, today is sunny and warm. 请问洗手间在哪里？Toiletはどこですか？店員さんに聞いてみよう。This sentence is intentionally very long to test the splitting functionality when it exceeds the maximum character limit, so it should be cut properly at the last punctuation within the allowed length. 项目进度需要加快，否则会delay；请大家focus on the timeline。あと、資料の提出もお願いします！Did you watch the latest episode of "鬼滅の刃"？It's absolutely amazing！！！また見たいですね…456。最后，祝大家Have a nice day！'''
# #
# # # print(tts.words_cut(words))
# # output_dir = "test"
# # os.makedirs(output_dir, exist_ok=True)
# # output_file = os.path.join(output_dir, f"tts_{int(time.time())}.wav")
# # print(output_file)
# #
# import asyncio
# from typing import  List,Callable,Any
# import random
# import uuid
#
#
# semaphore = asyncio.Semaphore(4)
#
# async def generate_and_play(texts):
#     # text是文本列表
#     if texts is None or texts==[]:
#          return None
#
#
#
# async def a_delay(text):
#     print(f"{text}任务开始！")
#     try:
#         delay = random.uniform(1, 5)  # 随机等待 1~5 秒
#         await asyncio.sleep(delay)
#         print(f"{text}任务结束！耗时 {delay:.2f}秒")
#     except asyncio.CancelledError:
#         print(f"{text}任务被取消！")
#
# async
# async def main():
#     tasks_manager=TasksManager(a_delay,4)
#     group1 = await tasks_manager.add_group([f"g1任务{i}" for i in range(10)])
#     group2 = await tasks_manager.add_group([f"g2任务{i}" for i in range(10)])
#     group3 = await tasks_manager.add_group([f"g3任务{i}" for i in range(10)])
#     await asyncio.sleep(3)
#     await tasks_manager.cancel_group(group1)
#     group4=await  tasks_manager.add_group([f"g4任务{i}" for i in range(10)])
#     await  asyncio.sleep(30)
#     tasks_manager.consumer_task.cancel()
#     try:
#         await tasks_manager.consumer_task
#     except asyncio.CancelledError:
#         pass
#     print("结束")
# asyncio.run(main())
#
#
#
#
#
#
#
#
from features.common.text_cutter import text_cutter
from features.llm.llm_qwen import chat_llm
from features.tts.TTS import TtsManager
from features.tts.tts_speech import tts_speech
import asyncio
text = '''【“我用中文回答："我很好，谢谢。 他说：“，"ありがとう。"，（谢谢）”，“然后他突然开始用英语说："I'm fine, thank you."”】'''

# text='''"你好，很高兴认识你！"她用中文说道。"こんにちは、はじめまして！"接着她又用日语说了一句。"Nice to meet you!"最后她用英语结束了这段对话。"Au revoir!"她突然想起了法语，又补充了一句。(再见！)然后她笑着说："See you next time!"这就是一个多语言交流的场景。"Merci beaucoup!"她又用法语表达了感谢。"Gracias!"西班牙语也来一句。"Dan'''
tts=TtsManager()
a,b=tts.words_cut( text),text_cutter( text)
print(a)
print(b)

for i,j in zip(a,b):
    if i!=j:
        print(i)
        print(j)
        print()


tts_speech(text)
