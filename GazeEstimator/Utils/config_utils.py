import json
import os

path="../config.json"
default_config={
    "left_eye":{
        "default":[-1,0],
        "landmarks":[
            [[-1,0],1],
            [[-1,0],1],
            [[-1,0],1],
            [[-1,0],1],
            [[-1,0],1]
        ],
    },
    "top_eye":{
        "default":[0,1],
        "landmarks":[
            [[0,1],1],
            [[0,1],1],
            [[0,1],1],
        ],
    },
    "right_eye":{
        "default":[1,0],
        "landmarks":[
            [[1,0],1],
            [[1,0],1],
            [[1,0],1],
            [[1,0],1],
            [[1,0],1]
        ],
    },
    "bottom_eye":{
        "default":[0,-1],
        "landmarks":[
            [[0,-1],1],
            [[0,-1],1],
            [[0,-1],1],
        ],
    },
    "limits":{
        "left":0.3,
        "top":0.7,
        "right":0.7,
        "bottom":0.3
    }
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
        for eye in ["left_eye","top_eye","right_eye","bottom_eye"]:
            for landmark in config[eye]["landmarks"]:
                if landmark["default"] is not list:
                    landmark["default"]=default_config[eye]["landmarks"]["default"]
                    raise TypeError("Point must be list")
    except Exception as e:
        return False
    return True
def set_config(config:dict):
    """Save the configuration to a file."""
    with open(path,"w") as file:
        json.dump(config,file)
def get_config() -> dict:
    """Get the configuration from a file."""
    if not os.path.exists(path):
        create_config()
    with open(path) as file:
        config=json.load(file)
        if check_config(config):
           set_config(config)
    return config


