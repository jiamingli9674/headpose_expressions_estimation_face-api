from flask import Flask, url_for
from models.user import User
from models.role import Role
from flask_security import Security, SQLAlchemyUserDatastore
import flask_admin
from views.views import *
from models.video import Video
from models.expression import Expression
from service.datebase import get_video_list
from views.forms import ExtendedRegisterForm

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_pyfile(config_name)
    from models import db
    db.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore, register_form=ExtendedRegisterForm)
    admin = flask_admin.Admin(
    app,
    'My Dashboard',
    base_template='my_master.html',
    template_mode='bootstrap4',
    )

    admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-user-circle-o', name="Roles"))
    admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
    admin.add_view(VideoView(Video, db.session, menu_icon_type='fa', menu_icon_value='fa-file-video-o', name="Video"))
    admin.add_view(ExpressionView(Expression, db.session, menu_icon_type='fa', menu_icon_value='fa-hand-peace-o', name="Expressions"))
    admin.add_view(ChartView(name="Chart", endpoint='chart', menu_icon_type='fa', menu_icon_value='fa-bar-chart',))
    admin.add_view(CalibrationView(name="Calibration", endpoint='calibration', menu_icon_type='fa', menu_icon_value='fa fa-arrows',))
    admin.add_view(PlayerView(name="Video", endpoint='play', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))
    
    return app, db, admin, security, user_datastore

    