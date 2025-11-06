import numpy as np
def get_single_weight(eye_landmark,eye_landmark_weight:list,pupil_landmark):
    """Calculate weight contribution from a single eye landmark and pupil position."""

    # prepare for calculation
    eye_position=np.array([eye_landmark.x,eye_landmark.y])
    pupil_position=np.array([pupil_landmark.x,pupil_landmark.y])
    weight=np.array(eye_landmark_weight)

    # Get how far from pupil to landmark
    position_delta = pupil_position-eye_position
    magnitude=pow(position_delta[0],2)+pow(position_delta[1],2)
    
    # Calculate weight
    result=weight*magnitude

    return result
def gaze_estimate_weight(left_eye_landmarks:list,top_eye_landmarks:list,right_eye_landmarks:list,bottom_eye_landmarks:list,pupil_landmark,config:dict)->tuple:
    """Estimate gaze direction weight based on eye landmarks and pupil position."""

    # Get weights for each landmark group fron config
    left_eye_landmarks_weights=config['left_eye']
    top_eye_landmarks_weights=config['top_eye']
    right_eye_landmarks_weights=config['right_eye']
    bottom_eye_landmarks_weights=config['bottom_eye']

    sum_weight=np.array([0.0,0.0])

    # Get weights for each landmark and sum them up
    if len(left_eye_landmarks)!=len(left_eye_landmarks_weights["landmarks"]):
        for eye_landmark in left_eye_landmarks:
            sum_weight+=get_single_weight(eye_landmark,left_eye_landmarks_weights["default"],pupil_landmark)
    else:
        for eye_landmark_index in range(len(left_eye_landmarks)):
            weight=[left_eye_landmarks_weights["landmarks"][eye_landmark_index][1]*left_eye_landmarks_weights["landmarks"][eye_landmark_index][0][0],
            left_eye_landmarks_weights["landmarks"][eye_landmark_index][1]*left_eye_landmarks_weights["landmarks"][eye_landmark_index][0][1]]
            sum_weight+get_single_weight(left_eye_landmarks[eye_landmark_index],weight,pupil_landmark)

    if len(right_eye_landmarks)!=len(right_eye_landmarks_weights["landmarks"]):
        for eye_landmark in right_eye_landmarks:
            sum_weight+=get_single_weight(eye_landmark,right_eye_landmarks_weights["default"],pupil_landmark)
    else:
        for eye_landmark_index in range(len(right_eye_landmarks)):
            weight=[right_eye_landmarks_weights["landmarks"][eye_landmark_index][1]*right_eye_landmarks_weights["landmarks"][eye_landmark_index][0][0],
            right_eye_landmarks_weights["landmarks"][eye_landmark_index][1]*right_eye_landmarks_weights["landmarks"][eye_landmark_index][0][1]]
            sum_weight+=get_single_weight(right_eye_landmarks[eye_landmark_index],weight,pupil_landmark)
    
    if len(top_eye_landmarks)!=len(top_eye_landmarks_weights["landmarks"]):
        for eye_landmark in top_eye_landmarks:
            sum_weight+=get_single_weight(eye_landmark,top_eye_landmarks_weights["default"],pupil_landmark)
    else:
        for eye_landmark_index in range(len(top_eye_landmarks)):
            weight=[top_eye_landmarks_weights["landmarks"][eye_landmark_index][1]*top_eye_landmarks_weights["landmarks"][eye_landmark_index][0][0],
            top_eye_landmarks_weights["landmarks"][eye_landmark_index][1]*top_eye_landmarks_weights["landmarks"][eye_landmark_index][0][1]]
            sum_weight+=get_single_weight(top_eye_landmarks[eye_landmark_index],weight,pupil_landmark)

    if len(bottom_eye_landmarks)!=len(bottom_eye_landmarks_weights["landmarks"]):
        for eye_landmark in bottom_eye_landmarks:
            sum_weight+=get_single_weight(eye_landmark,bottom_eye_landmarks_weights["default"],pupil_landmark)
    else:
        for eye_landmark_index in range(len(bottom_eye_landmarks)):
            weight=[bottom_eye_landmarks_weights["landmarks"][eye_landmark_index][1]*bottom_eye_landmarks_weights["landmarks"][eye_landmark_index][0][0],
            bottom_eye_landmarks_weights["landmarks"][eye_landmark_index][1]*bottom_eye_landmarks_weights["landmarks"][eye_landmark_index][0][1]]
            sum_weight+=get_single_weight(bottom_eye_landmarks[eye_landmark_index],weight,pupil_landmark)

    # Get average weight
    average_weight=sum_weight/16.0

    return tuple(average_weight.tolist())

def get_direction_5(gaze_direction_weight:tuple,config:dict)->int:
    """Get gaze direction as one of five categories based on weights and limits."""

    # Get limits from config
    left_limit=config["limits"]["left"]
    top_limit=config['limits']['top']
    right_limit=config['limits']['right']
    bottom_limit=config['limits']['bottom']
    
    x_weight=0;
    y_weight=0;

    # Calculate x and y weights
    if left_limit>gaze_direction_weight[0]>0:
        x_weight=-1
    elif right_limit<gaze_direction_weight[0]<1:
        x_weight=1

    if top_limit<gaze_direction_weight[1]<1:
        y_weight=1
    elif bottom_limit>gaze_direction_weight[1]>0:
        y_weight=-1
    
    # Get gaze direction
    if x_weight==0 and y_weight==0:
        result = 0
    elif x_weight==-1:
        result = 1 if y_weight==1 else 2
    elif x_weight==1:
        result = 4 if y_weight==1 else 3

    return result

