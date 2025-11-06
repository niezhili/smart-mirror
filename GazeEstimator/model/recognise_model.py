import dlib
import mediapipe as mp
import cv2
class recognise_model(object):
    def __init__(self):
        self.face_encoder = self.face_recognizer = cv2.FaceRecognizerSF.create(
                model="GazeEstimator/model/face_recognition_sface_2021dec.onnx",
                config="",
                backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
                target_id=cv2.dnn.DNN_TARGET_CPU
            )
        mp_face_mesh = mp.solutions.face_mesh
        self.feature_recognizer = mp_face_mesh.FaceMesh(refine_landmarks=True)
    def encode(self,img,bbox):
        """Encode the face in the image given the bounding box,which will be used in face matching"""
        standard_face = self.face_recognizer.alignCrop(img, bbox)
        face_features=self.face_recognizer.feature(standard_face)
        return face_features
    def match(self,face_features1,face_features2):
        """Match the two face features"""
        return self.face_encoder.match(face_features1, face_features2)
    def get_face_mesh(self,img,bbox):
        """Get the facial landmarks of the face in the image given the bounding box"""
        face=img[int(bbox[0]):int(bbox[0]+bbox[2]),int(bbox[1]):int(bbox[1]+bbox[3])]
        landmark = self.feature_recognizer.process(img).multi_face_landmarks[0].landmark
        return landmark;




