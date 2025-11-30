import time
import cv2
from threading import Thread

import numpy as np
from .utils import face_progress_utils
from .utils import config_utils
from .utils import gaze_estimate_utils

config=config_utils.get_config()
def get_face_from_image(img,reference_face_feature):
    face_boxes=face_progress_utils.get_multi_face_boses(img)
    if len(face_boxes)==0 or (len(face_boxes)>1 and reference_face_feature is None):
        return None

    target_face_box=None

    # Match target face
    if(len(face_boxes)==1):
        target_face_box=face_boxes[0]
    for face_box in face_boxes:
        face_feature=face_progress_utils.get_face_feature(img,face_box)
        if face_progress_utils.is_face_match(face_feature,reference_face_feature):
            target_face_box=face_box
            break
    if target_face_box is None:
        return None
    return target_face_box
def get_eye_from_face(face_landmarks,target_face_box):

    global config

    left_eye,right_eye=face_progress_utils.get_eye(face_landmarks)
    left_eye.config=config
    right_eye.config=config

    return left_eye,right_eye
def image_gaze_estimate_feature(img,reference_face_feature):
    """Get gaze direction from image and reference face feature."""

    target_face_box=get_face_from_image(img,reference_face_feature)
    if target_face_box==-1:
        return -1

    face_landmarks=face_progress_utils.get_face_landmarks(img,target_face_box)
    # Get eyes
    left_eye,right_eye=get_eye_from_face(face_landmarks,target_face_box)

    # Get gaze direction
    left_eye_direction_weight=left_eye.get_gaze_direction_weight()
    right_eye_direction_weight=right_eye.get_gaze_direction_weight()

    global config

    average_direction_weight=left_eye_direction_weight+right_eye_direction_weight/2
    gaze_direction=gaze_estimate_utils.get_direction_5(average_direction_weight,config)

    return gaze_direction
def image_gaze_estimate_img(img,reference_face_img):
    """Get gaze direction from image and reference face image."""
    reference_face_feature=None
    if reference_face_img is not None:
        reference_face_feature = face_progress_utils.get_face_single_feature(reference_face_img)
    image_gaze_estimate_feature(img,reference_face_feature)
class gaze_estimator(object):
    def __init__(self,reference_image,camera_index=0):
        self.camera=None
        self.reference_image_feature=face_progress_utils.get_face_single_feature(reference_image)
        self.camera_index=camera_index
        self.frame=None
        self.face_box=None
        self.face_landmarks=None
        self.left_eye=None
        self.right_eye=None
        self.thread=Thread(target=self.thread_get_frame)
    def start(self):
        """Start video capture from camera."""
        self.camera=cv2.VideoCapture(self.camera_index)
        self.thread.start()
    def get_frame_gaze_estimate(self):
        """Get gaze direction from the current camera frame."""
        if self.face_box is None:
            return -1
        if self.left_eye is None or self.right_eye is None:
            return -1
        left_eye_direction_weight=self.left_eye.get_gaze_direction_weight()
        right_eye_direction_weight=self.right_eye.get_gaze_direction_weight()

        global config

        average_direction_weight=(left_eye_direction_weight+right_eye_direction_weight)/2
        gaze_direction=gaze_estimate_utils.get_direction_5(average_direction_weight,config)

        return gaze_direction
        return -1
    def get_frame_gaze_estimate_weight(self):
        """Get gaze direction from the current camera frame."""
        if self.face_box is None:
            return -1
        if self.left_eye is None or self.right_eye is None:
            return -1
        left_eye_direction_weight=self.left_eye.get_gaze_direction_weight()
        right_eye_direction_weight=self.right_eye.get_gaze_direction_weight()

        global config

        average_direction_weight=(left_eye_direction_weight+right_eye_direction_weight)/2

        return average_direction_weight
        return -1
    def get_frame(self):
        return self.frame
    def thread_get_frame(self):
        while True:
            ret, frame = self.camera.read()
            if ret:
                frame=cv2.flip(frame,1)
                self.frame=frame
                self.face_box=get_face_from_image(frame,self.reference_image_feature)
                if self.face_box is None:
                    self.face_box=None
                    self.face_landmarks=None
                    self.left_eye,self.right_eye=None,None
                    time.sleep(0.01)
                    continue
                self.face_landmarks=face_progress_utils.get_face_landmarks(frame,self.face_box)
                if self.face_landmarks is None:
                     self.face_box=None
                     self.face_landmarks=None
                     self.left_eye,self.right_eye=None,None
                     time.sleep(0.01)
                     continue
                self.left_eye,self.right_eye=get_eye_from_face(self.face_landmarks,self.face_box)
            time.sleep(0.01)
    def get_face_box(self):
        return self.face_box
    def get_face_landmarks(self):
        return self.face_landmarks
    def get_eyes(self):
        return self.left_eye,self.right_eye
    def stop(self):
        """Release the camera resource."""
        self.thread.join()
        self.camera.release()
        self.thread=Thread(target=self.thread_get_frame)