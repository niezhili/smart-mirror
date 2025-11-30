from .utils import gaze_estimate_utils
import numpy as np
import cv2
class eye(object):
    def __init__(self,eye_landmarks,eye_rect,pupil,normal_weight):
        self.eye_landmarks = eye_landmarks
        self.eye_rect=eye_rect
        self.pupil = pupil
        self.normal_weight=normal_weight
        self.config=None
    def get_gaze_direction_weight(self):
        """Get gaze direction as one of five categories."""

        # Estimate gaze direction weight based on eye landmarks and pupil position.
        gaze_direction_weight=gaze_estimate_utils.gaze_estimate_weight(
            self.eye_landmarks,
            self.pupil,
            self.normal_weight)
        weight_map=np.array([[ [0.0,0.0,0.0] for _ in range(self.eye_rect[2])] for _ in range(self.eye_rect[3])],dtype=np.float32)
        for w in range(self.eye_rect[0],self.eye_rect[0]+self.eye_rect[2]):
            for h in [self.eye_rect[1],self.eye_rect[1]+self.eye_rect[3]-1]:
                point=np.array([w,h])
                weight=gaze_estimate_utils.gaze_estimate_weight(
                    self.eye_landmarks,
                    point,
                    self.normal_weight)
                weight_map[h-self.eye_rect[1]][w-self.eye_rect[0]][0:2]=weight
        for w in [self.eye_rect[0],self.eye_rect[0]+self.eye_rect[2]-1]:
            for h in range(self.eye_rect[1],self.eye_rect[1]+self.eye_rect[3]):
                point=np.array([w,h])
                weight=gaze_estimate_utils.gaze_estimate_weight(
                    self.eye_landmarks,
                    point,
                    self.normal_weight)
                weight_map[h-self.eye_rect[1]][w-self.eye_rect[0]][0:2]=weight
        maxarray=np.array([weight_map[...,0].max(),weight_map[...,1].max()])
        minarray=np.array([weight_map[...,0].min(),weight_map[...,1].min()])
        center=(maxarray+minarray)/2.0
        length=(maxarray-minarray)/2.0
        gaze_direction_weight=(gaze_direction_weight-center)/length
        return gaze_direction_weight
    def get_gaze_direction(self):
        gaze_direction_weight=self.get_gaze_direction_weight()
        # Get gaze direction as one of five categories based on weights and limits.
        gaze_direction=gaze_estimate_utils.get_direction_5(gaze_direction_weight,self.config)

        return gaze_direction
    def get_weight_map(self):
        weight_map=np.array([[ [0.0,0.0,0.0] for _ in range(self.eye_rect[2])] for _ in range(self.eye_rect[3])],dtype=np.float32)
        for w in range(int(self.eye_rect[0]),int(self.eye_rect[0]+self.eye_rect[2])):
            for h in range(self.eye_rect[1],self.eye_rect[1]+self.eye_rect[3]):
                point=np.array([w,h])
                weight=gaze_estimate_utils.gaze_estimate_weight(
                    self.eye_landmarks,
                    point,
                    self.normal_weight)
                weight_map[h-self.eye_rect[1]][w-self.eye_rect[0]][0:2]=weight
        maxarray=np.array([weight_map[...,0].max(),weight_map[...,1].max(),1])
        minarray=np.array([weight_map[...,0].min(),weight_map[...,1].min(),0])
        center=(maxarray+minarray-np.array([0,0,1]))/2.0
        length=(maxarray-minarray)/2.0
        weight_map=np.subtract(weight_map,center)/length

        mask = np.zeros((self.eye_rect[3], self.eye_rect[2]), dtype=np.uint8)
        poly = np.array([[lm[0]-self.eye_rect[0], lm[1]-self.eye_rect[1]] for lm in self.eye_landmarks], dtype=np.int32)
        cv2.fillPoly(mask, [poly], 1)

        return weight_map,mask
    def get_direction_weight_map(self):
        weight_map=np.array([[ [0.0,0.0,0.0] for _ in range(self.eye_rect[2])] for _ in range(self.eye_rect[3])],dtype=np.float32)
        for w in range(int(self.eye_rect[0]),int(self.eye_rect[0]+self.eye_rect[2])):
            for h in range(self.eye_rect[1],self.eye_rect[1]+self.eye_rect[3]):
                point=np.array([w,h])
                weight=gaze_estimate_utils.gaze_estimate_weight(
                    self.eye_landmarks,
                    point,
                    self.normal_weight)
                
                weight_map[h-self.eye_rect[1]][w-self.eye_rect[0]][0:2]=weight
        maxarray=np.array([weight_map[...,0].max(),weight_map[...,1].max(),1])
        minarray=np.array([weight_map[...,0].min(),weight_map[...,1].min(),0])
        center=(maxarray+minarray-np.array([0,0,1]))/2.0
        length=(maxarray-minarray)/2.0
        weight_map=np.subtract(weight_map,center)/length
        for h in range(self.eye_rect[1],self.eye_rect[1]+self.eye_rect[3]):
            for w in range(int(self.eye_rect[0]),int(self.eye_rect[0]+self.eye_rect[2])):
                direction=gaze_estimate_utils.get_direction_5(weight_map[h-self.eye_rect[1]][w-self.eye_rect[0]][0:2],self.config)
                weight_map[h-self.eye_rect[1]][w-self.eye_rect[0]][0:2]=direction
        mask = np.zeros((self.eye_rect[3], self.eye_rect[2]), dtype=np.uint8)
        poly = np.array([[lm[0]-self.eye_rect[0], lm[1]-self.eye_rect[1]] for lm in self.eye_landmarks], dtype=np.int32)
        cv2.fillPoly(mask, [poly], 1)

        return weight_map,mask





