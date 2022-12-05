from flask import *
from flask_sqlalchemy import SQLAlchemy
import urllib.request
import os
from werkzeug.utils import secure_filename
from flask import flash
from models import *
import uuid
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask import jsonify

UPLOAD_FOLDER = 'static/uploads/'
app.secret_key = "secretkey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ALLOWED_EXTENSTIONS = set(['png','jpg','jpeg','gif' , 'jfif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSTIONS

@app.route('/post')
@login_required
def post():
    shares = Share.query.filter_by(shared_to = current_user.id)
    return render_template('post.html',shares=shares)


@app.route('/users-follow')
@login_required
def follow_users():
    users = Users.query.filter(id != current_user.id).all()
    return render_template('users_follow.html',users=users)

@app.route('/shares/<post_id>')
@login_required
def shares(post_id):
    users = Users.query.all()
    return render_template('shares.html',users=users,post_id=post_id)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/upload_post', methods=['POST'])
@login_required
def upload_post():
    
    filepath = None
    if 'file' not in request.files:
        flash('no file part')
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4()) +  secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER']+filename)        
        file.save(filepath)
    
    description = request.form['desc']
    post = Posts(
        description=description, 
        image=filepath,
        user_id = current_user.id
        )

    db.session.add(post)
    db.session.commit()
    flash("Post uploaded")  

    return redirect('/post')



# posts show on home page.........................
@app.route('/home', methods=['GET','POST'])
def homepage():
    posts = Posts.query.order_by(Posts.date_created.desc()).all()
    return render_template('home.html',posts=posts)


# share  post
@app.route('/share-post', methods=['POST'])
def share():

    if request.method == 'POST':
        shared_by = current_user.id
        shared_to = request.form['shared_to']
        post_id = request.form['post_id']

        share = Share(
            shared_to=shared_to, 
            post_id=post_id,
            shared_by=shared_by
            )
        db.session.add(share)
        db.session.commit()
        return jsonify(
                    code=200,
                )


# follow and unfollow user
@app.route('/follow-user', methods=['POST'])
def follow():

    if request.method == 'POST':
        follower_id = current_user.id
        followed_id = request.form['followed_id']
        is_following = request.form['is_following']
        
        if is_following == 'true':

            follow = Follow(
                follower_id=follower_id, 
                Followed_id=followed_id
                )
            db.session.add(follow)
            db.session.commit()
            return jsonify(
                        code=200,
                    ) 

        Follow.query.filter_by(Followed_id=followed_id).filter_by(follower_id=follower_id).delete() 
        db.session.commit()
        return jsonify(
                        code=200,
                    )    
           
# like and dislike post
@app.route('/like-post', methods=['POST'])
def like():

    if request.method == 'POST':
        user_id = request.form['user_id']
        post_id = request.form['post_id']
        like = request.form['like']
        like_id = int(request.form['like_id'])

        # Like.query.delete()
        # db.session.commit()

        if like_id > 0:
            
            likeOjb = Likes.query.filter_by(id=like_id).first()
            likeOjb.user_id = user_id
            likeOjb.post_id = post_id

            if likeOjb.like:
               likeOjb.like=False 
            else :
               likeOjb.like = True 
            db.session.commit()
            return jsonify(
                    code=200,
                    like_id = like_id
                )

        like = Likes(
            user_id=user_id, 
            like=bool(like),
            post_id=post_id
            )
        db.session.add(like)
        db.session.commit()
        return jsonify(
                    code=200,
                    like_id = like_id
                )

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/signup' , methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        handle = request.form['handle']
        password = request.form['password']

        user = Users.query.filter_by(email=email).first()
        # If user exists, redirect to login page.
        if user:
            flash("User already exists") 
            return redirect(url_for('login')) 

        user = Users(
                    email=email, 
                    name=name,
                    handle=handle,
                    password=password
                    )

        db.session.add(user)
        db.session.commit()
        flash("User Registered! Sign in now") 
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/' , methods=['GET','POST'] )
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Users.query.filter_by(email=email).first()
        # Redirect to login if user does not exist or typed wrong password.
        if not user or not user.checkPassword(password):
            flash("Invalid login")
            return redirect(url_for('login'))

        # Otherwise log in user and redirect them to the homepage.
        login_user(user)
        return redirect(url_for('homepage'))

    return render_template('signin.html')


if __name__ == "__main__":
    app.run(debug=True)