from .Utils import gaze_estimate_utils

class eye(object):
    def __init__(self,left_eye_landmarks,top_eye_landmarks,right_eye_landmarks,bottom_eye_landmarks,eye_rect,pupil,config=None):
        self.left_eye_landmarks = left_eye_landmarks
        self.top_eye_landmarks = top_eye_landmarks
        self.right_eye_landmarks = right_eye_landmarks
        self.bottom_eye_landmarks = bottom_eye_landmarks
        self.eye_rect=eye_rect
        self.pupil = pupil
        self.config=config
    def get_gaze_direction(self):
        """Get gaze direction as one of five categories."""

        # Estimate gaze direction weight based on eye landmarks and pupil position.
        gaze_direction_weight=gaze_estimate_utils.gaze_estimate_weight(
            self.left_eye_landmarks,
            self.top_eye_landmarks,
            self.right_eye_landmarks,
            self.bottom_eye_landmarks,
            self.pupil,
            self.config)

        # Get gaze direction as one of five categories based on weights and limits.
        gaze_direction=gaze_estimate_utils.get_direction_5(gaze_direction_weight,self.config)

        return gaze_direction





