import cv2
import numpy as np
class dectecte_model(object):
    def __init__(self):
        self.face_detector = cv2.FaceDetectorYN.create(
            "GazeEstimator/model/face_detection_yunet_2023mar.onnx",
            "",
            input_size=[320, 320],
            score_threshold=0.6, 
            nms_threshold=0.3, 
            top_k=5000, 
            backend_id=0, 
            target_id=0)
    def detect(self,img):
        """Detect faces in the image and return bounding boxes."""
        h, w, _ = img.shape
        input_size=(w,h)
        self.face_detector.setInputSize(tuple(input_size))
        _,face_boxes = self.face_detector.detect(img)
        return np.empty(shape=(0, 5)) if face_boxes is None else face_boxes




