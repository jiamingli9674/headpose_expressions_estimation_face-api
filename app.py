#!venv/bin/python
import os
from flask import Flask, url_for, redirect, render_template, request, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, expose
from wtforms import PasswordField
import numpy as np
from util.headpose_estimation import get_angle

from config.config import STANDARD_LANDMARKS

# global variable

yaw_low = None
yaw_high = None
pitch_high = None
pitch_low = None

global_yaw = None
global_pitch = None

pose_num = 0


# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('config_.py')
db = SQLAlchemy(app)


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

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
    pitch, yaw, roll = get_angle(np.asarray(lm), image_points)
    global global_pitch, global_yaw
    global_pitch, global_yaw = pitch, yaw
    expressions = data['expressions']
    return dict(pitch=pitch, yaw=yaw, roll=roll, expressions=expressions)    

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    
    
class Expressions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    angry = db.Column(db.Float, nullable=False)
    disgusted = db.Column(db.Float, nullable=False)
    fearful = db.Column(db.Float, nullable=False)
    happy = db.Column(db.Float, nullable=False)
    neutral = db.Column(db.Float, nullable=False)
    sad = db.Column(db.Float, nullable=False)
    surprised = db.Column(db.Float, nullable=False)
    time_stamp = db.Column(db.Integer, nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user_expression = db.relationship('User', backref='experssion', lazy='joined')
    
    video_expression = db.relationship('Video', backref='expression', lazy='joined')
    
    def __repr__(self):
        return f'<{self.id} {self.expression} {self.score} {self.time_stamp} {self.video_id}>'
    
def get_or_create(table, name):
    record = table.query.filter_by(name=name).first()
    if record is None:
        record = table(name=name)
        db.session.add(record)
        db.session.commit()
    return record.id   

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


    # can_edit = True
    edit_modal = True
    create_modal = True    
    can_export = True
    can_view_details = True
    details_modal = True

class UserView(MyModelView):
    column_editable_list = ['email', 'first_name', 'last_name']
    column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    #form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list
    form_overrides = {
        'password': PasswordField
    }

class VideoView(MyModelView):
    column_editable_list = ['id', 'name']
    column_searchable_list = column_editable_list

class ExpressionView(MyModelView):
    pass
    

class CalibrationView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/calibration_view.html')
        
    
class PlayerView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/player_view.html')

# Flask views
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setpose')
def set_pose():
    global yaw_high, yaw_low, pitch_high, pitch_low, global_pitch, global_yaw
    if not pitch_low: #Up
        pitch_low = global_pitch
        return "0", 200
    elif not pitch_high: #Down
        pitch_high = global_pitch
        return "1", 200
    elif not yaw_low: #Left
        yaw_low = global_yaw
        return "2", 200
    else: #Right
        yaw_high = global_yaw
        return "3", 200
    
def check_setup():
    global yaw_high, yaw_low, pitch_high, pitch_low
    return yaw_high and yaw_low and pitch_high, pitch_low

@app.route("/checkpose")
def checkPose():
    global yaw_high, yaw_low, pitch_high, pitch_low, global_pitch, global_yaw
   
    pitch_tolerance, yaw_tolerance = 5, 5
    
    print(global_yaw)
    print(yaw_high)
    print(yaw_low)
    
    if (global_yaw < yaw_tolerance + yaw_high and global_yaw > yaw_low - yaw_tolerance):
        return 'good', 200

    # if (global_pitch < pitch_tolerance + pitch_high and global_pitch > pitch_low - pitch_tolerance and
    # global_yaw < yaw_tolerance + yaw_high and global_yaw > yaw_low - yaw_tolerance):
    #     return 'good', 200
    else:
        return 'bad', 200

@app.route("/resetpose")
def resetPose():
    global yaw_high, yaw_low, pitch_high, pitch_low
    yaw_high, yaw_low, pitch_high, pitch_low = None, None, None, None
    
    return "ok", 200
    

@app.route("/addvideo", methods=['GET', 'POST'])
def add_Video():
    data = request.get_json()
    video_id = get_or_create(Video, data['video'])
    return "ok", 200
    
    

@app.route("/result", methods=['POST', 'GET'])
def result():
    data = request.get_json()
    if 'video' not in data:
        info = get_landmarks_expressions(data)
        return info, 200
    else:
        info = get_landmarks_expressions(data)
        if not data['playing']:
            return info, 200
        info['video'] = data['video']
        info['time_stamp'] = data['timeStamp']
        user_id = current_user.get_id()
        video_id = get_or_create(Video, data['video'])
        exp = Expressions(**data['expressions'],time_stamp = data['timeStamp'], video_id=video_id, user_id=user_id)
        db.session.add(exp)
        db.session.commit()
        return info, 200

# Create admin
admin = flask_admin.Admin(
    app,
    'My Dashboard',
    base_template='my_master.html',
    template_mode='bootstrap4',
)

# Add model views
admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
admin.add_view(VideoView(Video, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Video"))
admin.add_view(ExpressionView(Expressions, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Expressions"))

admin.add_view(CalibrationView(name="Calibration", endpoint='calibration', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))
admin.add_view(PlayerView(name="Player", endpoint='player', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role]
        )

        db.session.commit()
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    # Start app
    app.run(debug=True)
