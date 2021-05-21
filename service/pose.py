from service import IMAGE_POINTS
from flask import session
import numpy as np
from util.headpose_estimation import get_angle

def get_pitch_yaw():
    if ('pitch' in session) and ('yaw' in session):
        print('in')
        return session['pitch'], session['yaw']
    else:
        return None, None
    
def set_headpose_limit():
    if 'pitch' not in session or 'yaw' not in session:
        return '4', 200
    else:
        if 'pitch_low' not in session: #Up
            session['pitch_low'] = session['pitch']
            return "0", 200
        elif 'pitch_high' not in session: #Down
            session['pitch_high'] = session['pitch']
            return "1", 200
        elif 'yaw_low' not in session: #Left
            session['yaw_low'] = session['yaw']
            return "2", 200
        elif 'yaw_high' not in session: #Right
            session['yaw_high'] = session['yaw']
            return "3", 200
        else:
            return '5', 200
        
    
def check_headpose_setting():
    return 'pitch_low' not in session \
        and 'pitch_high' in session \
        and 'yaw_low' in session \
        and 'yaw_high' in session

def reset_headpose_setting():
    if 'pitch_low' in session:
        session.pop('pitch_low', None)
    if 'pitch_high' in session:
        session.pop('pitch_high', None)
    if 'yaw_low' in session:
        session.pop('yaw_low', None)
    if 'yaw_high' in session:
        session.pop('yaw_high', None)
        
def get_headpose_limit():
    return session.get('pitch_low'), session.get('pitch_high'), session.get('yaw_low'), session.get('yaw_high')
       
def get_landmarks_expressions(data):
    landmarks = data['landmarks']['_positions']
    lm = []
    for i, landmark in enumerate(landmarks):
        x, y = landmark['_x'], landmark['_y']
        #print(f"{i} : ({x}, {y})")
        lm.append(np.asarray([float(x), float(y)]))
    pitch, yaw, roll = get_angle(np.asarray(lm), IMAGE_POINTS)   
    add_to_session(pitch, yaw)
    expressions = data['expressions']
    return dict(pitch=pitch, yaw=yaw, roll=roll, expressions=expressions)    
    
def add_to_session(pitch, yaw):
    session['pitch'] = pitch
    session['yaw'] = yaw
 
def check_pose():
    pitch, yaw = get_pitch_yaw()
    print(f'pitch:{pitch}, yaw:{yaw}')
    pitch_tolerance, yaw_tolerance = 5, 5
    pitch_low, pitch_high, yaw_low, yaw_high = get_headpose_limit()
    print(f'pitch:{pitch_low}-{pitch_high}, yaw:{yaw_low}-{yaw_high}')
    
    if not pitch:
        return 'not ready', 200
        
    else:
        if ((pitch > pitch_low - pitch_tolerance or pitch > pitch_high - pitch_tolerance) and
            yaw < yaw_tolerance + yaw_high and yaw > yaw_low - yaw_tolerance):
            return 'good', 200
        else:
            return 'bad', 200