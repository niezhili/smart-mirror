import cv2
import numpy as np
import threading
import time
from .reference import Reference
from .face_tracker import FaceTracker
from .gaze_estimator import GazeEstimator
from .calibrator import Calibrator
from .Camera import camera
from .dlib_face_recognizer import dlib_face_recognizer

class EyeTrackerAPI:
    """
    眼动仪库主API类
    实现需求中的第1,3,4,10-11步
    """
    def __init__(self, camera_index=0):
        """
        初始化EyeTrackerAPI
        
        Args:
            camera_index: 摄像头索引
        """
        camera.camera_threadings.start()
        self.camera = camera(camera_index)
        self.references = []  # 参考器列表
        self.gaze_estimator = GazeEstimator()
        self.calibrator = Calibrator()
        self.dlib_face_recognizer=dlib_face_recognizer()

        self.is_running = False
        self.processing_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # 帧率控制
        self.capture_fps = 30
        self.process_fps = 30
        
    def add_reference(self, reference):
        """
        添加参考器到API实例
        
        Args:
            reference: Reference实例
        """
        face_tracker = reference.get_face_tracker()
        if face_tracker is None:
            frame=reference.reference_images.copy()
            face_data = self.dlib_face_recognizer.detect(frame)[0]
            d,u,l,r=face_data.bottom(),face_data.top(), face_data.left(),face_data.right()
            face_image = frame[u:d,l:r]
            if self.dlib_face_recognizer is not None and face_image.size > 0:
                face = self.dlib_face_recognizer.predict(frame,face_data)
                face_feature = self.dlib_face_recognizer.encode(frame,face)
            else:
                raise ValueError("无法识别人脸")
            face_tracker = FaceTracker(face_feature, self.dlib_face_recognizer)
            reference.set_face_tracker(face_tracker)
        self.references.append(reference)
        
    def create_reference_from_image(self, image_path):
        """
        通过图像创建参考器实例
        
        Args:
            image_path: 图像路径
            
        Returns:
            Reference实例
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")
            
        reference = Reference(image)
        self.add_reference(reference)
        return reference
        
    def create_reference_from_images(self, image_paths):
        """
        通过多张图像创建参考器实例
        
        Args:
            image_paths: 图像路径列表
            
        Returns:
            Reference实例
        """
        images = []
        for path in image_paths:
            image = cv2.imread(path)
            if image is None:
                raise ValueError(f"无法读取图像: {path}")
            images.append(image)
            
        reference = Reference(images)
        self.add_reference(reference)
        return reference
        
    def start(self):
        """
        启动API实例，创建新的循环线程
        实现需求中的第3步
        """
        if self.is_running:
            return
            
        self.is_running = True
        
        # 创建摄像头读取线程
        # 实现需求中的第4步：创建新线程用于以固定频率读取摄像头图像数据

        # 创建处理线程
        self.processing_thread = threading.Thread(target=self._process_frames)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
    def stop(self):
        """
        停止API实例
        """
        self.is_running = False
        self.camera.release()
        if self.processing_thread:
            self.processing_thread.join()
    def _capture_frames(self):
        """
        以固定频率读取摄像头图像数据
        实现需求中的第4步
        """
        frame = self.camera.get_frame()
        self.current_frame = frame           
    def _process_frames(self):
        """
        处理帧数据
        """
        
        while self.is_running:
            try:
                self._capture_frames()
                if self.current_frame is None:
                    continue
                frame = self.current_frame.copy()
            
                # 使用FaceDetector在摄像头数据中检测面部
                # 实现需求中的第5步：使用Detector模型在摄像头数据中检测面部
            
                faces=self.dlib_face_recognizer.detect(frame)
            
                if faces is not None:
                    for reference in self.references:
                        for i, face_data in enumerate(faces):
                        
                            d,u,l,r=face_data.bottom(),face_data.top(), face_data.left(),face_data.right()
                            face_image = frame[u:d,l:r]
                            # 提取面部特征
                            face_feature = None
                        
                            if self.dlib_face_recognizer is not None and face_image.size > 0:
                                face = self.dlib_face_recognizer.predict(frame,face_data)
                                face_feature = self.dlib_face_recognizer.encode(frame,face)
                        
                            # 检查面部是否与参考器匹配
                            face_tracker = reference.get_face_tracker()
                        

                                # 检查是否匹配
                            is_match = face_tracker.is_face_match((face_image, face_feature))
                            if is_match:
                                reference.set_face_shape((l,u,r-l,d-u))
                                
                                # 获取眼部位置
                                # 实现需求中的第6步：使用cascade检测眼部，并降噪，使检测结果平滑且连续

                                info=self.dlib_face_recognizer.get_face_info(face_image,face,face_data)
                                reference.set_eye_info(info)
                                lec,rec=reference.eye_close
                                left_pupil, right_pupil = reference.pupil_points
                                left_eye, right_eye = reference.eye_center
                                left_rect,right_rect=reference.eyes
                                gaze_directions=None
                                if not lec:
                                    gaze_directions=l_direction = self.gaze_estimator.estimate_gaze_direction(
                                        left_pupil, left_eye,left_rect
                                    )
                                if not rec:
                                    gaze_directions=r_direction = self.gaze_estimator.estimate_gaze_direction(
                                        right_pupil, right_eye,right_rect
                                    )
                                if not lec and not rec:
                                    gaze_directions = (l_direction[0] + r_direction[0]) / 2, (l_direction[1] + r_direction[1]) / 2
                                if gaze_directions is not None:
                                    zone=self.gaze_estimator.estimate_gaze_zone(gaze_directions)
                                    reference.set_gaze_direction(gaze_directions)
                                    reference.set_zone(zone)
            except Exception as e:
                print(e)
                continue            
    def calibrate(self, calibration_points):
        """
        校准显示屏与摄像头的相对位置
        实现需求中的第9步：校准显示屏与摄像头的相对位置
        
        Args:
            calibration_points: 校准点列表 [(screen_x, screen_y, gaze_x, gaze_y), ...]
        """
        for point in calibration_points:
            self.calibrator.add_calibration_point(point[0], point[1], point[2], point[3])
            print(point)
        self.calibrator.calibrate()