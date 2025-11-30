import numpy as np
def get_single_weight(eye_landmark,eye_landmark_weight,pupil_landmark):
    """Calculate weight contribution from a single eye landmark and pupil position."""

    # prepare for calculation
    eye_position=np.array([eye_landmark.x,eye_landmark.y])
    pupil_position=np.array([pupil_landmark.x,pupil_landmark.y])
    weight=eye_landmark_weight

    # Get how far from pupil to landmark
    position_delta = pupil_position-eye_position
    magnitude=pow(position_delta[0],2)+pow(position_delta[1],2)
    
    # Calculate weight
    result=weight*magnitude

    return result
def gaze_estimate_weight(eye_landmarks,pupil_landmark,normal_weight)->tuple:
    """Estimate gaze direction weight based on eye landmarks and pupil position."""

    # Get weights for each landmark group fron config

    sum_weight=np.array([0.0,0.0])
    sub=np.subtract(eye_landmarks,pupil_landmark)
    length=np.linalg.norm(sub,axis=1)
    weight=length*normal_weight.T
    K=np.sum(\
        np.linalg.norm(\
            np.subtract(\
                eye_landmarks,pupil_landmark)
            ,axis=1)*(normal_weight.T),axis=1)
    # Get average weight
    average_weight=K/16.0

    return average_weight

def get_direction_5(gaze_direction_weight,config:dict)->int:
    """Get gaze direction as one of five categories based on weights and limits."""

    # Get limits from config
    left_limit=config["left"]
    top_limit=config['top']
    right_limit=config['right']
    bottom_limit=config['bottom']
    
    x_weight=0;
    y_weight=0;

    # Calculate x and y weights
    if right_limit>gaze_direction_weight[0]:
        x_weight=1
    elif left_limit<gaze_direction_weight[0]:
        x_weight=-1

    if top_limit<gaze_direction_weight[1]:
        y_weight=1
    elif bottom_limit>gaze_direction_weight[1]:
        y_weight=-1
    return(x_weight,y_weight)
    # Get gaze direction
    result = 0
    if x_weight==0 and y_weight==0: 
        result = 0
    elif x_weight==-1:
        result = 1 if y_weight==1 else 2
    elif x_weight==1:
        result = 4 if y_weight==1 else 3

    return result

