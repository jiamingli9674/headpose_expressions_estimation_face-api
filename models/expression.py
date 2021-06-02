from . import db

class Expression(db.Model):
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
    
    user_expression = db.relationship('User', backref='experssion')
    
    video_expression = db.relationship('Video', backref='expression')
    
    def __repr__(self):
        return f'<{self.id} {self.expression} {self.score} {self.time_stamp} {self.video_id}>'