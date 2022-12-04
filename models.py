from flask import Flask, render_template,request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy.orm import backref

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

class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(500),unique=True, nullable=True)
    description = db.Column(db.String(500), nullable=False)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("Users", backref=backref("Users", uselist=False))
    def getPostUser(self):
        user = Users.query.filter_by(id=self.user_id).first()
        if user:
            return user.name
        else :
            return "User"

    def getLikes(self):
        likes = Likes.query.filter_by(post_id=self.id).filter_by(like=True).count() 
        return likes       

    def isLikedByMe(self,current_user_id):
        like = Likes.query.filter_by(post_id=self.id).filter_by(user_id=current_user_id).filter_by(like=True).first() 
        if like:
            return True
        return False

    def getLikeID(self,current_user_id):
        like = Likes.query.filter_by(post_id=self.id).filter_by(user_id=current_user_id).first()
        if like:
            return like.id
        return 0

class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    handle = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50),unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def isFollowedByMe(self , current_user_id , followed_id):
        follow=Follow.query.filter_by(Followed_id=followed_id).filter_by(follower_id=current_user_id).first()  
        if follow:
           return True
        else :
           return False 

class Likes(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    like = db.Column(db.Boolean,default=False, nullable=False)

class Follow(db.Model):
    __tablename__ = 'follow'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    Followed_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Share(db.Model):
    __tablename__ = 'share'
    id = db.Column(db.Integer, primary_key=True)
    shared_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    shared_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


    def getPostID(self):
        return self.post_id.id
    def getSharedByUser(self,id):
        user = Users.query.filter_by(id=id).first()
        return user
    def getPostByID(self,id):
        return Posts.query.filter_by(id=id).first()

