import os
import secrets
from flask import render_template, url_for, flash, redirect, request, abort
from PIL import Image
from blogger import app, bcrypt, db, mail
from blogger.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from blogger.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("home.html", posts=posts)


@app.route('/about')
def about():
    users = User.query.all()
    return render_template("about.html", title='About Page', users=users)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(password=form.password.data).decode('UTF-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. LogIn now.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'You have been Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Login Failed. Please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_file(image_uploaded):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(image_uploaded.filename)
    pic_filename = random_hex + file_ext
    pic_path = os.path.join(app.root_path, 'static/profile_pics', pic_filename)

    output_size = (125, 125)
    resized_image = Image.open(image_uploaded)
    resized_image.thumbnail(output_size)

    resized_image.save(pic_path)
    return pic_filename


@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_pic.data:
            pic_fn = save_file(form.profile_pic.data)
            current_user.image_file = pic_fn
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account info has been updated!!!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_image = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html', title='User Account', profile_image=profile_image, form=form)


@app.route('/post/new', methods=['POST', 'GET'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!!!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='Create Post')


@app.route('/post/<int:idx>', methods=['POST', 'GET'])
@login_required
def view_post(idx):
    post = Post.query.get_or_404(idx)
    return render_template('post.html', title=post.title, post=post)


@app.route('/post/<int:idx>/update', methods=['POST', 'GET'])
@login_required
def update_post(idx):
    post = Post.query.get_or_404(idx)
    if post.author.id != current_user.id:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!!!', 'success')
        return redirect(url_for('new_post', idx=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route('/post/<int:idx>/delete', methods=['POST', 'GET'])
@login_required
def delete_post(idx):
    post = Post.query.get_or_404(idx)
    if post.author.id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!!!', 'success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("user_posts.html", posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@bloggerdemo.com', recipients=[user.email])
    msg.body = f"""To reset your password visit the link below:

{url_for('reset_token', token=token, _external=True)}

If you did not make this request, please just ignore this email and no changes will be made.
"""
    mail.send(msg)


# def send_reset_email(user):
#     smtp_server = "smtp.gmail.com"
#     port = 587
#     token = user.get_reset_token()
#     context = ssl.create_default_context()
#     try:
#         server = smtplib.SMTP(smtp_server, port)
#         server.ehlo()
#         server.starttls(context=context)
#         server.ehlo()
#         server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
#
#         msg = email.message.EmailMessage()
#         msg['Subject'] = 'Password Reset Request'
#         msg['From'] = app.config['MAIL_USERNAME']
#         msg['To'] = user.email
#         msg['Body'] = f"""To reset your password visit the link below:
#
# {url_for('reset_token', token=token, _external=True)}
#
# If you did not make this request, please just ignore this email and no changes will be made.
# """
#         # msg.set_content(message, subtype='html')
#         server.sendmail(msg['From'], [user.email], msg.as_string())
#
#     except Exception as e:
#         print(e)
#     finally:
#         server.quit()


@app.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(f'An email with instructions to reset password has been sent to your registered email.', 'info')
        return redirect(url_for('login'))
    return render_template("reset_request.html", title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash(f'Token invalid or expired!!!', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(password=form.password.data).decode('UTF-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!!! LogIn now.', 'success')
        return redirect(url_for('login'))
    return render_template("reset_token.html", title='Reset Password', form=form)
