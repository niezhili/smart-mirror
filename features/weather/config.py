import os
import yaml
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config/config.yaml")
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    Config = yaml.safe_load(f)
config=Config

class Config:
    API_KEY = config['weather']['weather_api_key']
    BASE_URL = "https://api.qweather.com/v7/weather/now"
