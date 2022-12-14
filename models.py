from flask import Flask, render_template,request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy.orm import backref
import hashlib


SALT = 'BlackPepper'

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username = 'ynotdoan',
    password = 'PASS12WORD',
    hostname = 'ynotdoan.mysql.pythonanywhere-services.com',
    databasename = 'ynotdoan$socialapp',
)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(300),unique=True, nullable=True)
    description = db.Column(db.String(300), nullable=False)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref=backref("User", uselist=False))
    def getPostUser(self):
        user = User.query.filter_by(id=self.user_id).first()
        if user:
            return user.name
        else :
            return "User"

    def getLikes(self):
        likes = Like.query.filter_by(post_id=self.id).filter_by(like=True).count()
        return likes

    def isLikedByMe(self,current_user_id):
        like = Like.query.filter_by(post_id=self.id).filter_by(user_id=current_user_id).filter_by(like=True).first()
        if like:
            return True
        return False

    def getLikeID(self,current_user_id):
        like = Like.query.filter_by(post_id=self.id).filter_by(user_id=current_user_id).first()
        if like:
            return like.id
        return 0

    def getImage(self):
        if self.image:
            filename = self.image.split('/')
            return filename[len(filename)-1]



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50) , nullable=True)
    email = db.Column(db.String(50),unique=True, nullable=False)
    user_password = db.Column(db.String(300), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Users %r>' % self.name

    def get_id(self):
        # Returns unicode that uniquely identifies the user.
        return self.id

    def is_authenticated(self):
        # Returns true if user has provided valid credentials
        return True

    def is_active(self):
        # Returns true if user's account had been authenticated and activated.
        return True

    def is_anonymous(self):
        # Returns true if user is annonymous
        return False

    @hybrid_property
    def password(self):
        # Hybrid property decorator allows expressions to work for python and SQL.
        return self.user_password

    @password.setter
    def password(self, p):
        # Salts and encodes password using SHA256. Then stores the hash password.
        p += SALT
        self.user_password = hashlib.sha256(p.encode()).hexdigest()

    def checkPassword(self, p):
        # Checks if user inputted password matched the one stored in record.
        p += SALT
        return self.user_password == hashlib.sha256(p.encode()).hexdigest()

    def isFollowedByMe(self, current_user_id , followed_id):
        follow=Follow.query.filter_by(Followed_id=followed_id).filter_by(follower_id=current_user_id).first()
        if follow:
           return True
        else:
           return False


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    like = db.Column(db.Boolean,default=False, nullable=False)

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    Followed_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shared_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    shared_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


    def getPostID(self):
        return self.post_id.id
    def getSharedByUser(self,id):
        user = User.query.filter_by(id=id).first()
        return user
    def getPostByID(self,id):
        return Post.query.filter_by(id=id).first()

