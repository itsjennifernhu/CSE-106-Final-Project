from flask import Flask, render_template,request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy.orm import backref

app = Flask(__name__)    
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.Text,unique=True, nullable=True)
    description = db.Column(db.Text, nullable=False)

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


            

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text , nullable=True)
    email = db.Column(db.Text,unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    
    def isFollowedByMe(self , current_user_id , followed_id):
        follow=Follow.query.filter_by(Followed_id=followed_id).filter_by(follower_id=current_user_id).first()  
        if follow:
           return True
        else :
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

