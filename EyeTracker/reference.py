from collections import deque
import numpy as np
class Reference:
    """
    参考器类，用于处理参考面部图像
    实现需求中的第2步：用户通过一张或多张图片创建参考器实例
    """
    def __init__(self, image):
        """
        初始化参考器
        
        Args:
            images: 参考图像（单张图像或图像列表）
        """  
        self.reference_images = image
        self.face_distance = 1.0  # 默认面部距离
        self.face_shape=(0,0,0,0)
        self.eyes=[(0,0,0,0),(0,0,0,0)]
        self.eye_center=[(0,0),(0,0)]
        self.eye_close=[True,True]
        self.pupil_points=[(0,0),(0,0)]
        self.gaze_direction=(0,0)
        self.zone=(0,0)
        self.face_tracker = None
    def set_eye_info(self,info):
        e=info["eye"]
        self.eyes=e["rect"]
        self.pupil_points=e["pupil"]
        self.eye_close=e["is_close"]
        self.eye_center=e["center"]
    def get_reference_faces(self):
        """
        获取参考面部图像
        
        Returns:
            参考面部图像列表
        """
        return self.reference_image
    def set_face_shape(self, face_shape):
        """
        设置面部形状
        
        Args:
            face_shape: 面部形状
        """
        self.face_shape = face_shape
    def get_face_shape(self):
        """
        获取面部形状
        
        Returns:
            面部形状
        """
        return self.face_shape
    def set_gaze_direction(self, direction):
        """
        设置视线方向
        
        Args:
            direction: 视线方向 (x, y) 
        """
        self.gaze_direction=direction;
    def get_gaze_direction(self):
        """
        获取视线方向
        
        Returns:
            视线方向 (x, y)
        """
        return self.gaze_direction
    def set_zone(self, zone):
        """
        设置视线区域
        
        Args:
            zone: 视线区域 (x, y)
        """
        self.zone=zone
    def get_zone(self):
        """
        获取视线区域
        
        Returns:
            视线区域 (x, y)
        """
        return self.zone
    def set_face_tracker(self, tracker):
        """
        设置面部追踪器
        
        Args:
            tracker: 面部追踪器
        """
        self.face_tracker = tracker
        
    def get_face_tracker(self):
        """
        获取面部追踪器
        
        Returns:
            面部追踪器
        """
        return self.face_tracker