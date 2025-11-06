import cv2
from .gaze_estimate import gaze_estimator
class gaze_estimator_api:
    def __init__(self,image_path):
        reference_image=cv2.imread(image_path)
        self.gaze_estimator=gaze_estimator(reference_image)
    def set_reference_image(self,image_path):
        self.gaze_estimator.reference_image=cv2.imread(image_path)
    def start(self):
        self.gaze_estimator.start()
    def get(self):
        return self.gaze_estimator.get_frame_gaze_estimate()
    def stop(self):
        self.gaze_estimator.stop()