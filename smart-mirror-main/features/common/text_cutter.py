import re

def text_cutter(text, language='auto'):

    if text is None or text == "":
        return []
    mixed_mode = False
    if language == 'auto':
        # 检测是否混合文本（同时包含中文和拉丁字母）
        has_chinese = re.search(r'[\u4e00-\u9fff]', text)
        has_latin = re.search(r'[a-zA-Z]', text)
        if has_chinese and has_latin:
            mixed_mode = True
        elif has_chinese:
            language = 'zh'
        elif re.search(r'[À-ÿ]', text):  # 法语字符
            language = 'fr'
        elif re.search(r'[ÄÖÜäöüß]', text):  # 德语字符
            language = 'de'
        elif re.search(r'[ぁ-ゔァ-ヴー]', text):  # 日语假名
            language = 'ja'
        else:
            language = 'en'

    # 中英混合模式处理
    if mixed_mode or (language == 'zh' and re.search(r'[a-zA-Z]', text)):
        # 组合中英文分割规则
        pattern = (
            r'(?<=[。！？；…])|'  # 中文标点
            r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+|'  # 英文标点（排除缩写）
            r'(?<=\.")\s+|(?<=\?")\s+|(?<=\!")'  # 处理带引号的句子
        )
        sentences = re.split(pattern, text)
        # 过滤空字符串并去除首尾空格
        sentences = [s.strip() for s in sentences if s.strip()]
        # 处理分割后可能残留的标点符号
        result = []
        for i, s in enumerate(sentences):
            if i > 0 and len(s) == 1 and s in '。！？.;!?':
                result[-1] += s
            else:
                result.append(s)
        return result

    if language == 'zh':
        # 中文句子分割: 根据中文标点符号分割
        sentences = re.split(r'([。！？；…]+)', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        # 合并分割符号和前面的句子
        result = []
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                result.append(sentences[i] + sentences[i + 1])
            else:
                result.append(sentences[i])
        return result

    elif language == 'ja':
        # 日语句子分割: 句号、感叹号、问号等
        sentences = re.split(r'([。！？]+)', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        # 合并分割符号和前面的句子
        result = []
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                result.append(sentences[i] + sentences[i + 1])
            else:
                result.append(sentences[i])
        return result

    elif language in ('en', 'fr', 'de'):
        # 英语、法语、德语的分割规则类似
        abbreviations = r'(?<!Mr)(?<!Mrs)(?<!Dr)(?<!Prof)(?<!Rev)(?<!Hon)\.'
        pattern = rf'(?<=[.!?]) +|{abbreviations} +'
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    else:
        # 默认使用通用分割
        sentences = re.split(r'(?<=[.!?]) +', text)
        return [s.strip() for s in sentences if s.strip()]


