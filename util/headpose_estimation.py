import cv2
import numpy as np
import math

def get_angle(landmarks, image_points):
    
    img_size = (480, 640)
    
    selected_points = [34, 9, 37, 46, 49, 55]
    
    landmarks = landmarks[selected_points]
    # image_points = np.array([five_points_dict['nose'],\
    #                             five_points_dict['left_eye'],\
    #                             five_points_dict['right_eye'],\
    #                             five_points_dict['mouse_left'],\
    #                             five_points_dict['mouse_right'],\
    #                         ])
    # 3D model points.
    model_points = image_points[selected_points]
    # Camera internals
    focal_length = img_size[1]
    center = (img_size[1] / 2, img_size[0] / 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]], dtype="double"
    )


    dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points,\
                                                                    landmarks,\
                                                                    camera_matrix,\
                                                                    dist_coeffs)
    # calculate rotation angles
    theta = cv2.norm(rotation_vector)
    # transformed to quaterniond
    w = np.cos(theta / 2)
    x = np.sin(theta / 2) * rotation_vector[0] / theta
    y = np.sin(theta / 2) * rotation_vector[1] / theta
    z = np.sin(theta / 2) * rotation_vector[2] / theta
    # quaterniondToEulerAngle
    ysqr = y * y
    xsqr = x * x
    zsqr = z * z
    # pitch (x-axis rotation)
    t0 = 2.0 * (w * x + y * z)
    t1 = 1.0 - 2.0 * (xsqr + ysqr)
    pitch = math.atan2(t0, t1)
    pitch = pitch * 180 / math.pi
    # yaw (y-axis rotation)
    t2 = 2.0 * (w * y - z * x)
    t2 = 1.0 if t2 > 1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    yaw = math.asin(t2)
    yaw = yaw * 180 / math.pi
    # roll (z-axis rotation)
    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (ysqr + zsqr)
    roll = math.atan2(t3, t4)
    roll = roll * 180 / math.pi
    if roll > 90:
        roll = (roll - 180) % 180
    if roll < -90:
        roll = (roll + 180) % 180
    angle_dict = {"pitch": pitch,\
                            "yaw":   yaw,\
                            "roll":  roll}
    return angle_dict