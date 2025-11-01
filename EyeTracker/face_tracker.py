import cv2
import numpy as np
class FaceTracker:
    """
    面部追踪器类，用于追踪特定目标人脸
    """
    def __init__(self, origin_face_feature, dlib_face_recognizer):
        """
        初始化面部追踪器
        
        Args:
            origin_face_feature: 目标人脸特征
            face_recognizer: 人脸识别器实例
        """
        self.color = (np.random.randint(0, 256), 
                      np.random.randint(0, 256), 
                      np.random.randint(0, 256))
        self.face_recognizer = dlib_face_recognizer
        self.ownface = origin_face_feature
        
    def update(self, img, box):
        """
        更新面部追踪器
        
        Args:
            img: 图像
            box: 人脸边界框
        """
        if box is None:
            self.eye_detector.update(img, None, None, None)
            return
            
        x, y, w, h = map(int, box[:4])
        img = cv2.rectangle(img, (x, y), (x + w, y + h), self.color, 2)
        
    def is_face_match(self, face):
        """
        检查人脸是否匹配目标人脸
        
        Args:
            face: (图像, 特征)元组
            
        Returns:
            bool: 是否匹配
        """
        img, feature = face
        if feature is None or self.ownface is None:
            return False
            
        similarity = self.face_recognizer.match(self.ownface, feature)
        return similarity > 0.6