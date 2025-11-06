import cv2
from .Utils import face_progress_utils
from .Utils import config_utils
from .Utils import gaze_estimate_utils

config=config_utils.get_config()

def image_gaze_estimate_feature(img,reference_face_feature):
    """Get gaze direction from image and reference face feature."""
    face_boxes=face_progress_utils.get_multi_face_boses(img)
    if len(face_boxes)==0 or (len(face_boxes)>1 and reference_face_feature==None):
        return -1

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
        return -1
    
    global config

    # Get eyes
    face_landmarks=face_progress_utils.get_face_landmarks(img,target_face_box)
    left_eye,right_eye=face_progress_utils.get_eye(face_landmarks)
    left_eye.config=config
    right_eye.config=config

    # Get gaze direction
    left_eye_direction=left_eye.get_gaze_direction()
    right_eye_direction=right_eye.get_gaze_direction()
    if(left_eye_direction==0 or right_eye_direction==0):
        return 0;
    else:
        return left_eye_direction

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
    def start(self):
        """Start video capture from camera."""
        self.camera=cv2.VideoCapture(self.camera_index)
    def get_frame_gaze_estimate(self):
        """Get gaze direction from the current camera frame."""
        ret, frame = self.camera.read()
        if ret:
            gaze_direction = image_gaze_estimate_feature(frame,self.reference_image_feature)
            return gaze_direction
        return -1
    def stop(self):
        """Release the camera resource."""
        self.camera.release()