from app import create_app
from flask import render_template, request
from flask_security import current_user
from service.pose import *
from service.datebase import *

app = create_app('./config/app_config.py')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setpose', methods=['GET', 'POST'])
def set_pose():
    data = request.get_json()
    pitch = data['pitch']
    yaw = data['yaw']
    set_headpose_limit(pitch, yaw)
    return "ok", 200


@app.route("/checkpose")
def checkPose():
    return check_headpose_setting()

@app.route("/resetpose")
def resetPose():
    return reset_headpose_setting()
    

@app.route("/addvideo", methods=['GET', 'POST'])
def add_Video():
    def get_video_code(url):
        return url.split("=")[-1]
    data = request.get_json()
    #TODO

@app.route("/result", methods=['POST', 'GET'])
def result():
    data = request.get_json()
