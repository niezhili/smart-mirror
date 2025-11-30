import cv2
import numpy as np
from .gaze_estimate import gaze_estimator
class gaze_estimator_debug_api:
    def __init__(self,image_path):
        reference_image=cv2.imread(image_path)
        self.gaze_estimator=gaze_estimator(reference_image,0)
    def set_reference_image(self,image_path):
        self.gaze_estimator.reference_image=cv2.imread(image_path)
    def start(self):
        self.gaze_estimator.start()
    def get(self):
        return self.gaze_estimator.get_frame_gaze_estimate()
    def get_weight(self):
        return self.gaze_estimator.get_frame_gaze_estimate_weight()
    def get_frame(self):
        return self.gaze_estimator.get_frame()
    def get_face_box(self):
        return self.gaze_estimator.get_face_box()
    def get_eye_rect(self,left_eye,right_eye):
        
        if left_eye is None or right_eye is None:
            return None,None
        left_eye_rect=left_eye.eye_rect
        right_eye_rect=right_eye.eye_rect
        return left_eye_rect,right_eye_rect
    def get_eye_weight_map(self,left_eye,right_eye):

        if left_eye is None or right_eye is None:
            return None,None
        left_eye_weight_map,left_eye_mask=left_eye.get_direction_weight_map()
        right_eye_weight_map,right_eye_mask=right_eye.get_direction_weight_map()
        return left_eye_weight_map,left_eye_mask,right_eye_weight_map,right_eye_mask
    def get_debug_image(self):
        base_image=self.get_frame()
        if base_image is None:
            return -1;
        base_image=base_image.copy()
        face_box=self.get_face_box()
        if face_box is None:
            return base_image
        image_2=cv2.rectangle(base_image, rec=tuple([int(n) for n in face_box[:4]]), color=(255, 0, 0),thickness= 2)
        left_eye,right_eye= self.gaze_estimator.get_eyes()
        if left_eye is None or right_eye is None:
            return base_image
        left_eye_weight_map,left_eye_mask,right_eye_weight_map,right_eye_mask=self.get_eye_weight_map(left_eye,right_eye)
        left_eye_rect,right_eye_rect=self.get_eye_rect(left_eye,right_eye)
        left_eye_weight_map*=255
        right_eye_weight_map*=255
        left_eye_weight_map=left_eye_weight_map.astype(int)
        right_eye_weight_map=right_eye_weight_map.astype(int)
        left_eye_weight_map=np.maximum(left_eye_weight_map, 0)
        right_eye_weight_map=np.maximum(right_eye_weight_map, 0)
        image_2=cv2.rectangle(image_2, rec=tuple(left_eye_rect), color=(255, 0, 0),thickness= 2)
        image_2=cv2.rectangle(image_2, rec=tuple(right_eye_rect), color=(255, 0, 0),thickness= 2)
        image_2[left_eye_rect[1]:left_eye_rect[1]+left_eye_rect[3],left_eye_rect[0]:left_eye_rect[0]+left_eye_rect[2]][left_eye_mask==1]=left_eye_weight_map[left_eye_mask==1]
        image_2[right_eye_rect[1]:right_eye_rect[1]+right_eye_rect[3],right_eye_rect[0]:right_eye_rect[0]+right_eye_rect[2]][right_eye_mask==1]=right_eye_weight_map[right_eye_mask==1]
        return image_2
    def stop(self):
        self.gaze_estimator.stop()