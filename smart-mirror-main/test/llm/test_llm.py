from features.llm.llm_qwen import chat_llm
while 1:
    text=input("请输入：")
    print(chat_llm(text))