import numpy as np
from ..eye import eye
from ..model.detecte_model import dectecte_model
from ..model.recognise_model import recognise_model

detector=dectecte_model()
recogniser=recognise_model()

#region Face Utils
def get_multi_face_boses(img):
    """Get multi face from image."""
    global detector

    faces=detector.detect(img)
    return faces

def get_single_face_box(img):
    """Get single face from image."""
    face=get_multi_face_boses(img)[0]
    return face

def get_face_feature(img,face_box):
    """Get face feature from image and face box."""
    global recogniser

    face_feature=recogniser.encode(img,face_box)
    return face_feature

def get_face_single_feature(img):
    """Get face feature from image."""
    face_box=get_single_face_box(img)
    face_feature=get_face_feature(img,face_box)
    return face_feature

def get_face_landmarks(img,face_box):
    """Get eye landmarks from face landmarks."""
    global recogniser

    face_landmarks=recogniser.get_face_mesh(img,face_box)
    return face_landmarks

def is_face_match(face_feature1,face_feature2,threshold=0.6):
    """Get face feature from image and face box."""
    global recogniser

    similarity = recogniser.match(face_feature1, face_feature2)
    return similarity>=threshold

#region Eye Utils
def get_eye(face_landmarks):
    """Get eye objects from face landmarks."""

    # Get eye landmarks and pupil
    left_eye_landmarks, right_eye_landmarks, left_pupil_landmark, right_pupil_landmark=get_eye_landmarks(face_landmarks)

    # group landmarks into top, bottom, left, right
    left_eye_left_landmarks, left_eye_top_landmarks, left_eye_right_landmarks, left_eye_bottom_landmarks, right_eye_left_landmarks, right_eye_top_landmarks, right_eye_right_landmarks, right_eye_bottom_landmarks=eye_landmarks_group(left_eye_landmarks, right_eye_landmarks)

    # Get eye rect
    left_eye_rect, right_eye_rect=get_eye_rect(left_eye_landmarks, right_eye_landmarks)

    # Get eye objects
    left_eye=eye(left_eye_landmarks=left_eye_left_landmarks, 
        top_eye_landmarks=left_eye_top_landmarks, 
        right_eye_landmarks=left_eye_right_landmarks, 
        bottom_eye_landmarks=left_eye_bottom_landmarks,
        eye_rect=left_eye_rect,
        pupil=left_pupil_landmark)
    right_eye=eye(left_eye_landmarks=right_eye_left_landmarks, 
        top_eye_landmarks=right_eye_top_landmarks, 
        right_eye_landmarks=right_eye_right_landmarks, 
        bottom_eye_landmarks=right_eye_bottom_landmarks,
        eye_rect=right_eye_rect,
        pupil=right_pupil_landmark)
    return left_eye, right_eye
def get_eye_landmarks(face_landmarks):
    """Get eye landmarks and pupil"""
    left_eye_landmarks_index=[33,246,161,160,159,158,157,173,133,155,154,153,145,144,163,7]
    left_eye_landmarks=[face_landmarks[p] for p in left_eye_landmarks_index]
    left_pupil_landmark=face_landmarks[468]

    right_eye_landmarks_index=[263,466,388,387,386,385,384,398,362,382,381,380,374,373,390,249]
    right_eye_landmarks=[face_landmarks[p] for p in right_eye_landmarks_index]
    right_pupil_landmark=face_landmarks[473]
    return left_eye_landmarks, right_eye_landmarks, left_pupil_landmark, right_pupil_landmark
def eye_landmarks_group(left_eye_landmarks,right_eye_landmarks):
    """group landmarks into top, bottom, left, right"""
    left_eye_left_landmarks=left_eye_landmarks[:3]+left_eye_landmarks[-1:-2:-1]
    left_eye_top_landmarks=left_eye_landmarks[3:6]
    left_eye_right_landmarks=left_eye_landmarks[6:11]
    left_eye_bottom_landmarks=left_eye_landmarks[11:14]

    right_eye_left_landmarks=right_eye_landmarks[6:11]
    right_eye_top_landmarks=right_eye_landmarks[3:6]
    right_eye_right_landmarks=right_eye_landmarks[:3]+right_eye_landmarks[-1:-2:-1]
    right_eye_bottom_landmarks=right_eye_landmarks[11:14]
    return left_eye_left_landmarks, left_eye_top_landmarks, left_eye_right_landmarks, left_eye_bottom_landmarks, right_eye_left_landmarks, right_eye_top_landmarks, right_eye_right_landmarks, right_eye_bottom_landmarks
def get_eye_rect(left_eye_landmarks, right_eye_landmarks):
    """Get eye rect"""

    #Get four edges of eye rectangles
    left_eye_top=min(left_eye_landmarks,key=lambda x:x.y).y
    left_eye_bottom=max(left_eye_landmarks,key=lambda x:x.y).y
    left_eye_left=min(left_eye_landmarks,key=lambda x:x.x).x
    left_eye_right=max(left_eye_landmarks,key=lambda x:x.x).x

    right_eye_top=min(right_eye_landmarks,key=lambda x:x.y).y
    right_eye_bottom=max(right_eye_landmarks,key=lambda x:x.y).y
    right_eye_left=min(right_eye_landmarks,key=lambda x:x.x).x
    right_eye_right=max(right_eye_landmarks,key=lambda x:x.x).x
    
    # Get eye width and height
    left_eye_width=left_eye_right-left_eye_left
    left_eye_height=left_eye_bottom-left_eye_top

    right_eye_width=right_eye_right-right_eye_left
    right_eye_height=right_eye_bottom-right_eye_top

    # Get eye rect
    left_eye_rect=(left_eye_left,left_eye_top,left_eye_width,left_eye_height)
    right_eye_rect=(right_eye_left,right_eye_top,right_eye_width,right_eye_height)
    return left_eye_rect, right_eye_rect
