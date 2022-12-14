from flask import *
from flask_sqlalchemy import SQLAlchemy
import urllib.request
import os
from werkzeug.utils import secure_filename
from flask import flash
from models import *
import uuid
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask import jsonify


UPLOAD_FOLDER = 'static/uploads/'
app.secret_key = "cairocoders-edalan"
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
    users = User.query.filter(id != current_user.id).all()
    return render_template('users_follow.html',users=users)

@app.route('/shares/<post_id>')
@login_required
def shares(post_id):
    users = User.query.all()
    return render_template('shares.html',users=users,post_id=post_id)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/upload_post', methods=['POST'])
@login_required
def upload_post():
    if request.method == 'POST':
        filepath = None
        if 'file' not in request.files:
            flash('no file part')
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = str(uuid.uuid4()) +  secure_filename(file.filename)
            # filepath = os.path.join(app.config['UPLOAD_FOLDER']+filename)
            # file.save(filepath)
            # os.path.join(uploads_dir, secure_filename(input.filename))
            # file.save(os.path.join(UPLOAD_FOLDER, secure_filename(file.filename)))
            basedir = os.path.abspath(os.path.dirname(__file__))
            filepath = os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        description = request.form['desc']
        p = Post(
            description=description,
            image=filepath,
            user_id = current_user.id
            )

        db.session.add(p)
        db.session.commit()
        flash("Post uploaded")

        return redirect('/post')



# posts show on home page.........................
@app.route('/home', methods=['GET','POST'])
def show():
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template('home.html',posts=posts)


@app.route('/myfeed', methods=['GET', 'POST'])
@login_required
def getFeed():
    # if request.method == 'POST':
    my_feed = {}
    feed = db.session.query(Follow, Post) \
        .order_by(Post.date_created.desc()) \
        .filter(Follow.follower_id==current_user.id) \
        .filter(Post.user_id==Follow.Followed_id).all()
    # for f in feed:
    #     print(f)
    #     my_feed[f.Post.get_id()] = {
    #         "date":f.Post.getDate(),
    #         "likes":f.Post.getLikes(),
    #         "user":f.Post.getUser(),
    #         "handle":f.Post.getHandle(),
    #         "content":f.Post.getDescription(),
    #         "date":f.Post.getDate(),
    #         "title":f.Post.getTitle()
    #     }
        # return jsonify(my_feed)

    return render_template('myfeed.html', posts=feed)


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

            likeOjb = Like.query.filter_by(id=like_id).first()
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

        like = Like(
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
    return User.query.get(int(user_id))


@app.route('/signup' , methods=['GET','POST'])
def signup():

    if request.method == 'POST':

        email = request.form['email']
        name = request.form['name']
        password = request.form['password']

        u = User.query.filter_by(email=email).first()
        if u:
            flash("User already exists")
            return redirect('/')

        u = User(
            email=email,
            name=name,
            password=password
            )

        db.session.add(u)
        db.session.commit()
        flash("User Registered! Sign in now")
        return redirect('/')

    return render_template('signup.html')



@app.route('/' , methods=['GET','POST'] )
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        u = User.query.filter_by(email=email).first()
        if not u or not u.checkPassword(password):
            flash("Invalid login")
            return redirect('/')

        login_user(u)
        return redirect('/home')
    return render_template('sign_in.html')






if __name__ == "__main__":
    app.run(debug=True)