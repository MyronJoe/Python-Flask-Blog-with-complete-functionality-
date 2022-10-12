import os
import secrets
from PIL import Image
from app import app, bcrypt, db
from flask import render_template, url_for, redirect, flash, request, abort, send_from_directory
from app.form import RegistrationForm, LoginForm, PostForm, UpdateAccountForm, SearchForm
from app.models import User, Post, Comment
from flask_login import login_user, logout_user, current_user, login_required
from flask_ckeditor import upload_success, upload_fail


@app.route('/')
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)


# get Entertainment post depending on the category
@app.route("/category/Entertainment")
def category_Entertainment():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category='Entertainment').order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('all_category.html', posts=posts, legend='Entertainment', url='category_Entertainment')


# get politic post depending on the category
@app.route("/category/Politics")
def category_Politics():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category='Politics').order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('all_category.html', posts=posts, legend='Politics', url='category_Politics')


# get sports post depending on the category
@app.route("/category/Sports")
def category_Sports():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category='Sports').order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('all_category.html', posts=posts, legend='Sports', url='category_Sports')


# passing the search form into the layout
@app.context_processor
def layout():
    form = SearchForm()
    return dict(form=form)# routing the search form
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Post.query
    if form.validate_on_submit():
        # get data from form
        post.searched = form.searched.data
        # query the data base
        posts = posts.filter(Post.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Post.title).all()
    return render_template('search.html', form=form, searched=post.searched, posts=posts)


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin == False:
        return redirect(url_for('home'))
    image_file = url_for('static', filename='profile_pics/' + current_user.profile_img)
    return render_template('dashboard.html', image_file=image_file)


@app.route('/table')
@login_required
def table():
    if current_user.is_admin == False:
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('user_table.html', users=users)


@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if current_user.is_admin == False:
        return redirect(url_for('home'))
    form = RegistrationForm()
    # getting data from form and adding to database
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=True)
        db.session.add(user)
        db.session.commit()
        flash('Your Admin account was created successfully', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account was created successfully', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # check if the user is already logged in so that u cant create account while logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    # creating the instance of LoginForm
    if form.validate_on_submit():
        # getting data from form and query the database to see if the user have an account
        user = User.query.filter_by(email=form.email.data).first()
        # check the hashed_password and finally login the user
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # here directs the user to the page he wanted to log in to b4 he was redirected to login
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        # if the login details are wrong, this section runs
        else:
            flash('Check if your inputs are correct', 'danger')
    return render_template('login.html', form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# User Account route
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.profile_img = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account have been updated successfully', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.profile_img)
    return render_template('account.html', image_file=image_file, form=form)


# funtion for uploading blog picture
def blog_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

# Creating new post route
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.is_admin == False:
        return redirect(url_for('home'))
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            image_pic = blog_picture(form.picture.data)
            picture_file = image_pic
        user = Post(title=form.title.data, content=form.content.data, category=form.category.data, author=current_user,
                    image_file=picture_file)
        db.session.add(user)
        db.session.commit()
        flash('Your post have been uploaded successfully', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form, legend='Creat Post')


# get the post on a single page and slugify the url
@app.route('/post/<int:post_id>/<string:slug>', methods=['GET', 'POST'])
def post(post_id, slug):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    post.views += 2
    db.session.commit()
    if request.method == 'POST':
        name = request.form.get('name')
        message = request.form.get('message')
        comment = Comment(name=name, message=message, post_id=post.id)
        db.session.add(comment)
        post.comments += 1
        db.session.commit()
        return redirect(request.url)

    return render_template('post.html', post=post, comments=comments)


@app.route('/post/<int:post_id>/<string:slug>/comments')
def comments(post_id, slug):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    return render_template('comments.html', post=post, comments=comments)

# Update a post
@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        if form.picture.data:
            image_pic = blog_picture(form.picture.data)
            picture_file = image_pic
        post.image_file = picture_file
        db.session.commit()
        flash('Your post have been updated successfully!', 'success')
        return redirect(url_for('post', post_id=post.id, slug=post.slug))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category
        form.picture.data = post.image_file
    return render_template('create_post.html', form=form, legend='Update Post')


# delete a post
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post have been deleted successfully!', 'info')
    return redirect(url_for('home', post_id=post.id))


# get all user posts, post by an idividual author
@app.route("/user/<string:username>")
def user_post(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('user_post.html', posts=posts, user=user)


# get all post depending on the category
@app.route("/category/<string:category>")
def category_post(category):
    page = request.args.get('page', 1, type=int)
    post = Post.query.filter_by(category=category).first_or_404()
    posts = Post.query.filter_by(category=category).order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('category_post.html', posts=posts, post=post)


@app.route('/files/<path:filename>')
def uploaded_files(filename):
    path = 'static/img'
    return send_from_directory(path, filename)


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    # Add more validations here
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    f.save(os.path.join(app.root_path, 'static/img', f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return upload_success(url, filename=f.filename)  # return upload_success call