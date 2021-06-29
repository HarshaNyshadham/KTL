from source import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,current_user
from source import login
from flask_admin.contrib.sqla import ModelView


class adminView(ModelView):
      def is_accessible(self):
        if(current_user.username=='admin'):
          return True


class user(UserMixin ,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    firstName = db.Column(db.String(64),unique=True)
    lastName = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True)#, unique=True)
    phone = db.Column(db.String(120), index=True)#, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False



@login.user_loader
def load_user(id):
    return user.query.get(int(id))


class score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id1 = db.Column(db.String(64), index=True)
    player_id2 = db.Column(db.String(64), index=True)
    deadline = db.Column(db.Date, index=True)
    score = db.Column(db.String(120), index=True,default="")
    division = db.Column(db.String(2),index=True)
    level=db.Column(db.Float,index=True)

class pointTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(64))
    played = db.Column(db.Integer,default=0)
    win = db.Column(db.Integer,default=0)
    loss = db.Column(db.Integer,default=0)
    tie = db.Column(db.Integer,default=0)
    bonus = db.Column(db.Integer,default=0)
    points = db.Column(db.Integer,default=0)
    xrating = db.Column(db.Integer,default=1000)
    gamesplayed= db.Column(db.Integer,default=0)
    gameswon= db.Column(db.Integer,default=0)
    set1played= db.Column(db.Integer,default=0)
    set1won= db.Column(db.Integer,default=0)
    set2played= db.Column(db.Integer,default=0)
    set2won= db.Column(db.Integer,default=0)
    set3played= db.Column(db.Integer,default=0)
    set3won= db.Column(db.Integer,default=0)

#     def __repr__(self):
#         return '<User {}>'.format(self.player_id)

class players(db.Model):
    player_id=db.Column(db.String(64), index=True,primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))

