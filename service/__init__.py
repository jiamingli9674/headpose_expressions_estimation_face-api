from config.config import STANDARD_LANDMARKS
import numpy as np

from util.headpose_estimation import get_angle


IMAGE_POINTS = []
for line in STANDARD_LANDMARKS.split('\n'):
    x, y, z = map(float, line.split(','))
    IMAGE_POINTS.append(np.asarray([x, y, z]))
    
IMAGE_POINTS = np.asarray(IMAGE_POINTS)
