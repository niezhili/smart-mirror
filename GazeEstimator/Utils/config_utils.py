import json
import os
import numpy as np
path=os.path.dirname(os.path.dirname(__file__))+"\\config.json"
default_config={
        "left":0.3,
        "top":0.7,
        "right":0.7,
        "bottom":0.3
}
def create_config():
    """Create a default configuration file."""
    global default_config
    config=default_config
    set_config(config)
def check_config(config:dict):
    """Check the validity of the configuration file."""
    global default_config
    try:
        for eye in ["left","top","right","bottom"]:
            if not isinstance(config[eye],float):
                raise TypeError("Point must be list")
    except Exception as e:
        return False
    return True
def set_config(config:dict):
    """Save the configuration to a file."""
    global path
    with open(path,"w") as file:
        json.dump(config,file)
def get_config() -> dict:
    """Get the configuration from a file."""
    global path
    if not os.path.exists(path):
        create_config()
    try:
        with open(path) as file:
            config=json.load(file)
            if not check_config(config):
               raise TypeError("Point must be list")
    except Exception as e:
        create_config()
        config=default_config
    return config


