from flask import Flask, render_template, request, Response
from util.headpose_estimation import get_angle
import numpy as np
from config.config import STANDARD_LANDMARKS
app = Flask(__name__)


import numpy as np

image_points = []
for line in STANDARD_LANDMARKS.split('\n'):
    x, y, z = map(float, line.split(','))
    image_points.append(np.asarray([x, y, z]))
    
image_points = np.asarray(image_points)
    
def get_landmarks_expressions(data):
    landmarks = data['landmarks']['_positions']
    lm = []
    for i, landmark in enumerate(landmarks):
        x, y = landmark['_x'], landmark['_y']
        #print(f"{i} : ({x}, {y})")
        lm.append(np.asarray([float(x), float(y)]))
    print(get_angle(np.asarray(lm), image_points))
    print("====")
    
    expressions = data['expressions']
    for exp, score in expressions.items():
        print(f"{exp} : {score}")
    print("====")


@app.route("/")
def index():
   return render_template("index.html")

@app.route("/result", methods=['POST', 'GET'])
def result():
    data = request.get_json()
    get_landmarks_expressions(data)
    return Response("success", 200)

if __name__ == '__main__':
   app.run(debug = True)