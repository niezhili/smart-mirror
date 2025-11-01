"""
EyeTracker 眼动仪库

这是一个完整的眼动追踪库，包含以下主要组件：

Modules:
- Calibrator: 校准器，用于校准屏幕与摄像头的相对位置
- EyeDetector: 眼部检测器，用于检测和追踪眼睛
- EyeTrackerAPI: 眼动仪库主API类
- FaceDetector: 面部检测器
- FaceRecognizer: 面部识别器
- FaceTracker: 面部追踪器类，用于追踪特定目标人脸
- GazeEstimator: 视线估计器
- Reference: 参考器类，用于处理参考面部图像
"""

# 从各模块导入主要类
from .calibrator import Calibrator
from .eye_tracker_api import EyeTrackerAPI
from .face_tracker import FaceTracker
from .gaze_estimator import GazeEstimator
from .reference import Reference
from .Camera import camera
from .api import api

# 定义包的公开接口
__all__ = [
    "Calibrator",
    "EyeTrackerAPI",
    "FaceTracker",
    "GazeEstimator",
    "Reference"
]

# 包版本信息
__version__ = "1.0.0"
__author__ = "EyeTracker Development Team"