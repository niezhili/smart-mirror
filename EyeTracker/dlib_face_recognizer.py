import dlib
import cv2
import numpy as np
import time
import mediapipe as mp
class dlib_face_recognizer(object):
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("EyeTracker/model/shape_predictor_68_face_landmarks.dat")
        self.encoder = dlib.face_recognition_model_v1('EyeTracker/model/dlib_face_recognition_resnet_model_v1.dat')
        self.face_recognizer = cv2.FaceRecognizerSF.create(
                model="EyeTracker/model/face_recognition_sface_2021dec.onnx",
                config="",
                backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
                target_id=cv2.dnn.DNN_TARGET_CPU
            )
        mp_face_mesh = mp.solutions.face_mesh
        mp_face_detection = mp.solutions.face_detection
        self.face_detection=mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
        self.face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
        self.mp_drawing = mp.solutions.drawing_utils

    def detect(self,img):
        start_time = time.time()
        detector = self.detector
        faces = detector(img, 0)
        elapsed = time.time() - start_time
        
        return faces
    def predict(self,img, face):
        shape=self.predictor(img, face)
        return shape
    def encode(self,image,shape):
        face = dlib.get_face_chip(image, shape)
        face_descriptor = self.face_recognizer.feature(face)
        return face_descriptor
    def match(self,face1,face2):
        return self.face_recognizer.match(face1, face2)
    def get_face_info(self,img,shape,face_data):
        eye_points=self.get_eye_points(shape)
        eye_rects=self.get_eye_rects(eye_points)
        
        
        landmarks = self.face_mesh.process(img).multi_face_landmarks[0].landmark
        is_eyes_close=self.close_eye_detect(landmarks)
        pupil_points = self.get_pupil_points(landmarks)
        eye_centers=self.get_eye_centers(landmarks)
        l,u,w,h=face_data.left(),face_data.top(),face_data.width(),face_data.height()
        return {"eye":{"rect":eye_rects,
        "center":
        ((l+eye_centers[0][0]*w,u+eye_centers[0][1]*h),
        (l+eye_centers[1][0]*w,u+eye_centers[1][1]*h)),
        "is_close":is_eyes_close,
        "pupil":((l+pupil_points[0].x*w,u+pupil_points[0].y*h),(l+pupil_points[1].x*w,u+pupil_points[1].y*h))}}
    def get_eye_points(self,shape):
        sp=shape.parts()
        eye_points = (sp[36:42], sp[42:48])
        return eye_points
    def get_eye_rects(self,eyes):
       l_u=min(eyes[0],key=lambda x:x.y).y
       l_d=max(eyes[0],key=lambda x:x.y).y
       l_l=min(eyes[0],key=lambda x:x.x).x
       l_r=max(eyes[0],key=lambda x:x.x).x
       r_u=min(eyes[1],key=lambda x:x.y).y
       r_d=max(eyes[1],key=lambda x:x.y).y
       r_l=min(eyes[1],key=lambda x:x.x).x
       r_r=max(eyes[1],key=lambda x:x.x).x
       return ((l_l,l_u,l_r-l_l,l_d-l_u),(r_l,r_u,r_r-r_l,r_d-r_u))
    def get_eye_centers(self,landmarks):
        le=[33,246,161,160,159,158,157,173,133,155,154,153,145,144,163,7]
        #le=(np.mean([landmarks[p].x for p in le]), np.mean([landmarks[p].y for p in le]), np.mean([landmarks[p].z for p in le]))
        le=(np.mean([landmarks[p].x for p in [33,133]]), np.mean([landmarks[p].y for p in [33,133]]), np.mean([landmarks[p].z for p in [33,133]]))
        re=[263,466,388,387,386,385,384,398,362,382,381,380,374,373,390,249]
        #re=(np.mean([landmarks[p].x for p in re]), np.mean([landmarks[p].y for p in re]), np.mean([landmarks[p].z for p in re]))
        re=(np.mean([landmarks[p].x for p in [263,362]]), np.mean([landmarks[p].y for p in [263,362]]), np.mean([landmarks[p].z for p in [263,362]]))
        return (le,re)                             
    def close_eye_detect(self,landmarks):
        le=[33,246,161,160,159,158,157,173,133,155,154,153,145,144,163,7]
        le=(np.sum([landmarks[le[p]].y for p in range(9,16)])-np.sum([landmarks[le[p]].y for p in range(1,8)]))/7/(landmarks[le[8]].x-landmarks[le[0]].x)
        le=True if le<0.08 else False
        re=[263,466,388,387,386,385,384,398,362,382,381,380,374,373,390,249]
        re=(np.sum([landmarks[re[p]].y for p in range(9,16)])-
        np.sum([landmarks[re[p]].y for p in range(1,8)])
        )/7/(landmarks[re[0]].x-landmarks[re[8]].x)
        re=True if re<0.08 else False
        return (le,re)
    
    def get_pupil_points(self,landmarks):
        """
        获取瞳孔位置
        """
        return (landmarks[468], landmarks[473])




