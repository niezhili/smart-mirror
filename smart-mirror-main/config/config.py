import os
import yaml

# 获取配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

# 读取配置文件
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 导出配置
globals()['config'] = config