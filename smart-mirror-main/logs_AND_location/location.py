import os
from pathlib import Path
logs_str=os.path.dirname(os.path.abspath(__file__))
logs_path=Path(logs_str)
root_path=logs_path.parent
root_str=root_path.as_posix()