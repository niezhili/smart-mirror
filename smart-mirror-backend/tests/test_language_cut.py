import re
import re

import re

import re


def split_by_language(text):
    # 匹配两类：
    # 1. 汉字 + 日语字符（平假名、片假名）的组合块
    # 2. 拉丁字母块（含德语变音）
    pattern = r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]+|[a-zA-ZäöüßÄÖÜ][a-zA-ZäöüßÄÖÜ\'\-_]*[a-zA-ZäöüßÄÖÜ]?'

    matches = re.findall(pattern, text)

    # 过滤空格，保留有意义的部分
    return [m.strip() for m in matches if m.strip()]
# 示例
text = '今dytvifh日は世界ですWelt再见ekfiewfiuweuilhlih'
result = split_by_language(text)
print(result)