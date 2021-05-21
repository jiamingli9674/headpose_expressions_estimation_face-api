from wtforms import StringField
from wtforms.validators import DataRequired
from flask_security import RegisterForm



class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
    
