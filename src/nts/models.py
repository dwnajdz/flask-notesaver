import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from nts import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.Text, nullable=False, default='User')
    notes = db.relationship('Note', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default=id)
    image_file = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.datetime.now)
    content = db.Column(db.Text, nullable=False)
    privacy = db.Column(db.Text, default='Public')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def get_share_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'note_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_share_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            note_id = s.loads(token)['note_id']
        except:
            return None
        return Note.query.get(note_id)

    def __repr__(self):
        return f"Note('{self.title}', '{self.date_posted}')"
