from math import pi

from flask.globals import session
from werkzeug.utils import redirect
import views
from app import create_app
from views.views import PlayerView
from flask import render_template, request, jsonify
from flask_security import current_user
from flask_admin import helpers as admin_helpers
from flask import url_for,render_template, request
from service.datebase import *
from service.pose import *
from views.views import BaseView
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
    return dict(video_list = get_video_list(), user_list = get_user_list())
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chart/<user>/<video>', methods=['GET', 'POST'])
def chart(user, video):
    checked = request.get_json()['checked']
    print(checked)
    user_id = get_user_id_by_name(user)
    video_id = get_video_id_by_title(video)
    
    data = get_exps_by_user_and_video(user_id, video_id, checked)
    return jsonify(**data)


@app.route('/admin/play/<code>')
def play(code):
    session['video_code'] = code
    return redirect('/admin/play/')

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
    print(data)
    video_id = add_video(data['video_code'])
    return 'ok', 200

@app.route("/result", methods=['POST', 'GET'])
def result():
    data = request.get_json()
    return save_data(data)


if __name__ == '__main__':
    
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db(app, db, user_datastore)
    # with app.app_context():
    #     for video in get_video_list():
    #         admin.add_view(PlayerView(name=video['title'], endpoint='play/'+video['code'], menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))
    #     # Start app
    app.run(debug=True)