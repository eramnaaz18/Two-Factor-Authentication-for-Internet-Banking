from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from auth import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    address = db.Column(db.String(120), unique=False, nullable=False)
    account = db.Column(db.String(14), unique=True, nullable=False)
    debit = db.Column(db.String(16), unique=True, nullable=False)
    balance = db.Column(db.String(16), unique=False, nullable=True)
    image_file = db.Column(db.String(120), nullable=False, default='default.jpg')
    face_reco_id = db.Column(db.String(60), nullable=False, default = 'default.jpg')
    password = db.Column(db.String(60), nullable=False)
    #posts = db.relationship('Post', backref='author', lazy=True)

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
        return f"User('{self.username}', '{self.email}', '{self.phone}', '{self.address}', '{self.image_file}')"

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    acctype = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    customers = db.relationship(User)
    status = db.Column(db.String(250), nullable=False)
    message =  db.Column(db.String(250))
    last_update = db.Column(db.DateTime)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
db.create_all()