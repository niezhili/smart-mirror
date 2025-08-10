import re
import emoji
def text_clean(text):
    ##
    # 文本清洗，过滤表情包、网址等
    # #
    text = emoji.replace_emoji(text, replace='')
    text = re.sub(r'(\*{1,2}|_)(.+?)(\*{1,2}|_)', r'\2', text)
    text = re.sub(r'!\[.*?]\(.*?\)', '', text)
    text = re.sub(r'$$(.+?)$$(?:$$.*?$$)?', r'\1', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[*-]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'https?://\S+', '', text)
    return text
