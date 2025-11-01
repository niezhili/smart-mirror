import numpy as np
import cv2
class GazeEstimator:
    """
    视线估计器
    实现需求中的第7-8步：分割出眼部图像，经历阈值分割以及连通域检测，
    提取最大的连通域作为瞳孔，根据瞳孔和眼部中心的相对位置计算视线方向
    """
    def __init__(self):
        """
        初始化视线估计器
        """
        pass
        
    def estimate_gaze_direction(self, pupil, eye,eye_rect):
        """
        根据瞳孔和眼部中心的相对位置计算视线方向
        
        Args:
            left_pupil: 左瞳孔位置
            right_pupil: 右瞳孔位置
            left_eye: 左眼边界框
            right_eye: 右眼边界框
            
        Returns:
            视线方向向量
        """
        gaze_directions = []
        
        # 计算左眼视线方向
        if pupil is not None and eye is not None:
            eye_center_x,eye_center_y = eye
            dx = (pupil[0] - eye_center_x)/eye_rect[2]*2
            dy = -(pupil[1] - eye_center_y)/eye_rect[3]*2
        return (dx, dy)
    def estimate_gaze_zone(self,direction):
        """
         根据视线方向判断视线区域
         
         Args:
             direction: 视线方向向量
             
         Returns:
             视线区域
         """
        if direction[1]>0.5:
           y=1
        elif direction[1]<0.33:
           y=-1
        else:
           y=0
        if direction[0]>0.12:
           x=1
        elif direction[0]<-0.12:
           x=-1
        else:
           x=0
        return (x,y)

