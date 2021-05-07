import cv2
import numpy as np
import math

def get_angle(landmarks, image_points):
    
    img_size = (480, 640)
    
    selected_points = [34, 9, 37, 46, 49, 55]
    
    landmarks = landmarks[selected_points]

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
    
    rmat, _ = cv2.Rodrigues(rotation_vector) 
    return rotationMatrixToEulerAngles(rmat) 
    # calculate rotation angles
    # theta = cv2.norm(rotation_vector)
    # # transformed to quaterniond
    # w = np.cos(theta / 2)
    # x = np.sin(theta / 2) * rotation_vector[0] / theta
    # y = np.sin(theta / 2) * rotation_vector[1] / theta
    # z = np.sin(theta / 2) * rotation_vector[2] / theta
    # # quaterniondToEulerAngle
    # ysqr = y * y
    # xsqr = x * x
    # zsqr = z * z
    # # pitch (x-axis rotation)
    # t0 = 2.0 * (w * x + y * z)
    # t1 = 1.0 - 2.0 * (xsqr + ysqr)
    # pitch = math.atan2(t0, t1)
    # pitch = pitch * 180 / math.pi
    # # yaw (y-axis rotation)
    # t2 = 2.0 * (w * y - z * x)
    # t2 = 1.0 if t2 > 1.0 else t2
    # t2 = -1.0 if t2 < -1.0 else t2
    # yaw = math.asin(t2)
    # yaw = yaw * 180 / math.pi
    # # roll (z-axis rotation)
    # t3 = 2.0 * (w * z + x * y)
    # t4 = 1.0 - 2.0 * (ysqr + zsqr)
    # roll = math.atan2(t3, t4)
    # roll = roll * 180 / math.pi
    # if roll > 90:
    #     roll = (roll - 180) % 180
    # if roll < -90:
    #     roll = (roll + 180) % 180
    
    # if pitch < 0:
    #     pitch = -(180+pitch)
    # else:
    #     pitch = 180 - pitch
    
    
    #return int(pitch), int(yaw), int(roll)

def rotationMatrixToEulerAngles(R) : 
    # assert(isRotationMatrix(R)) 
    
    # To prevent the Gimbal Lock it is possible to use 
    # a threshold of 1e-6 for discrimination 
    sy = math.sqrt(R[0,0] * R[0,0] + R[1,0] * R[1,0]) 
    singular = sy < 1e-6 
    
    if not singular : 
        x = math.atan2(R[2,1] , R[2,2]) 
        y = math.atan2(-R[2,0], sy) 
        z = math.atan2(R[1,0], R[0,0]) 
    else : 
        x = math.atan2(-R[1,2], R[1,1]) 
        y = math.atan2(-R[2,0], sy) 
        z = 0 
        
    return to_degree(x), to_degree(y), to_degree(z)

def to_degree(a):
    return int(a * 180 / 3.14)