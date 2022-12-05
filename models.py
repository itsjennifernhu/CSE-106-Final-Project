from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref
from datetime import datetime
import hashlib

SALT = 'BlackPepper'

app = Flask(__name__)
# Info for SQLAlchemy to connect to database.
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username = 'ynotdoan',
    password = 'PASS12WORD',
    hostname = 'ynotdoan.mysql.pythonanywhere-services.com',
    databasename = 'ynotdoan$socialapp',
)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299 # Parameter that closes unused connections after 299 seconds.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
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

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    handle = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50),unique=True, nullable=False)
    user_password = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Users %r>' % self.handle

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

