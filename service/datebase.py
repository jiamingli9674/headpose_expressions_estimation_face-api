from models import db
from models.video import Video
from models.user import User
from models.role import Role
from service.pose import get_landmarks_expressions
from flask_security import current_user
from models.expression import Expression
from config.config import VIDEO_LIST
from flask_security.utils import encrypt_password

import random

def get_or_create(table, code):
    record = table.query.filter_by(code=code).first()
    if record is None:
        record = table(code=code)
        db.session.add(record)
        db.session.commit()
    return record.id   

def get_video_id_by_title(title):
    video = Video.query.filter_by(title=title).first()
    return video.id
    
def get_user_id_by_name(name):
    first_name = name.split(' ')[0]
    user = User.query.filter_by(first_name=first_name).first()
    return user.id

def get_user_list():
    user_list = []
    for user in User.query.all():
        if not user.first_name:
            first_name = ''
        else:
            first_name = user.first_name
        if not user.last_name:
            last_name = ''
        else:
            last_name = user.last_name
        name = first_name + " " + last_name
        user_list.append(dict(name = name))
    return user_list

def get_video_list():
    video_list = []
    for video in Video.query.all():
        video_list.append(dict(code = video.code, title = video.title))
    return video_list

def get_exps_by_user_and_video(user_id, video_id, checked, time_span = 60):
    # result = Expression.query.filter_by(user_id = user_id, video_id = video_id).order_by(Expression.time_stamp).all()
    # record_num = result[-1].time_stamp // time_span + 1
    # time_stamps_scores = [[0]*7]
    # for r in result:
    #     scores = [r.angry, r.disgusted, r.fearful,
    #             r.happy, r.neutral, r.sad, r.surprised]
    #     exp_index = scores.index(max(scores))
    #     time_stamp = r.time_stamp // time_span
    #     time_stamps_scores[time_stamp][exp_index] += 1
    # votes = []
    # for i, t in enumerate(time_stamps_scores):
    #     score_sume = sum(time_stamps_scores[i])
    #     votes.append([s/score_sume for s in time_stamps_scores[i]])
    # votes = list(map(list, zip(*votes)))
    def get_element_by_index(l, index):
        return [l[i] for i in index]
    
    def get_random_scores(num):
        return [random.randint(0, 10) for _ in range(num)]
    record_num = 10
    time_stamps_scores = [get_random_scores(7) for _ in range(record_num)]
    votes = time_stamps_scores
    # for i, t in enumerate(time_stamps_scores):
    #     score_sume = sum(time_stamps_scores[i])
    #     votes.append([int(s/score_sume * 100) for s in time_stamps_scores[i]])
    votes = list(map(list, zip(*votes)))
    
    lables = [str(i) for i in range(record_num)]
    
    tag = ['Angry', 'Disgusted', 'Fearful', 'Happy', 'Neutral', 'Sad', 'Surprised']
    backgroundColor = ['rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)',
                'rgba(255, 0, 0, 0.2)']
    borderColor = [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)',
                'rgba(255, 0, 0, 1)'
            ]
    borderWidth = 1
    datasets = [dict(label=tag[i], data=votes[i], backgroundColor=backgroundColor[i], borderColor=borderColor[i], borderWidth=borderWidth) for i in checked]
    data = dict(labels = lables, datasets = datasets)
    print(data)
    return data 



def add_video(video_code):
    video_id = get_or_create(Video, video_code)
    return "ok", 200

def save_data(data):
    if 'video' not in data:
        info = get_landmarks_expressions(data)
        print("no video code")
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
        
        for video in VIDEO_LIST:
            v = Video(code=video['code'], title=video['title'])
            db.session.add(v)
        db.session.commit()
        
    return

