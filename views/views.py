from . import MyModelView
from flask_admin import BaseView, expose

from wtforms import PasswordField

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
    

class CalibrationView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/calibration.html')
        
    
class PlayerView(BaseView):
    def is_visible(self):
        return False
    @expose('/')
    def play(self):
        code = self.endpoint.split('/')[-1]
        return self.render('admin/player.html', code=code)
