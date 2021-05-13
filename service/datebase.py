from models import db
from models.video import Video
from models.user import User
from models.role import Role
from service.pose import get_landmarks_expressions
from flask_security import current_user
from models.expression import Expression

from flask_security.utils import encrypt_password

def get_or_create(table, name):
    record = table.query.filter_by(name=name).first()
    if record is None:
        record = table(name=name)
        db.session.add(record)
        db.session.commit()
    return record.id   

def get_exps_by_user_and_video(user_id, video_id, time_span = 60):
    result = Expression.query.filter_by(user_id = user_id, video_id = video_id).order_by(Expression.time_stamp).all()
    record_num = result[-1].time_stamp // time_span + 1
    

def add_video(video_code):
    video_id = get_or_create(Video, video_code)
    return "ok", 200

def save_data(data):
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
        exp = Expression(**data['expressions'],time_stamp = data['timeStamp'], video_id=video_id, user_id=user_id)
        db.session.add(exp)
        db.session.commit()
        return info, 200
    
def build_sample_db(app, db, user_datastore):
    """
    Populate a small db with some example entries.
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
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

