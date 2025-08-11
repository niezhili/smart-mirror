from log.location import root_str
import yaml
import os
CONFIG_PATH = os.path.join(root_str, "config/config.yaml")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)