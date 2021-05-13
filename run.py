from math import pi
from app import create_app
from config.config import VIDEO_LIST
from flask import render_template, request
from flask_security import current_user
from flask_admin import helpers as admin_helpers
from flask import url_for,render_template, request
from service.datebase import build_sample_db, add_video
from service.pose import check_pose, get_headpose_limit, get_pitch_yaw, set_headpose_limit, check_headpose_setting, reset_headpose_setting, get_landmarks_expressions

import os 

app, db, admin, security, user_datastore = create_app(os.path.join(os.getcwd(), 'config/app_config.py'))


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )
    
@app.context_processor
def inject():
    return dict(video_list = VIDEO_LIST)
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play/<code>')
def play(code):
    return render_template('admin/player.html', code=code)

@app.route('/setpose')
def set_pose():
    return set_headpose_limit()
    
@app.route('/calibration')
def calibration():
    return render_template('admin/calibration.html')

@app.route("/checkpose")
def checkPose():
    return check_pose()

@app.route("/resetpose")
def resetPose():
    reset_headpose_setting()
    return 'ok', 200
    

@app.route("/addvideo", methods=['GET', 'POST'])
def add_Video():
    data = request.get_json()
    video_id = add_video(data['video_code'])
    return 'ok', 200

@app.route("/result", methods=['POST', 'GET'])
def result():
    data = request.get_json()
    return get_landmarks_expressions(data), 200


if __name__ == '__main__':
    
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db(app, db, user_datastore)

    # Start app
    app.run(debug=True)