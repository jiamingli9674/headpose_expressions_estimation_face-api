from . import MyModelView
from flask_admin import BaseView, expose
from flask import session
from wtforms import PasswordField
from flask_security import current_user

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
    column_editable_list = ['code', 'title']
    column_searchable_list = column_editable_list

class ExpressionView(MyModelView):
    pass
    
class ChartView(BaseView):
    def is_accessible(self):
        if not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False
    @expose('/')
    def index(self):
        return self.render('admin/chart.html')
        

class CalibrationView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/calibration.html')
        
    
class PlayerView(BaseView):
    def is_visible(self):
        return False
    @expose('/')
    def play(self):
        code = session['video_code']
        return self.render('admin/player.html', code=code)
