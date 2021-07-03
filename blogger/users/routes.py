from flask import Blueprint, url_for, flash, redirect, render_template, request
from flask_login import current_user, login_user, logout_user, login_required

from blogger import bcrypt, db
from blogger.models import User, Post
from blogger.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from blogger.users.utils import send_reset_email, save_file

users = Blueprint('users', __name__)


@users.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(password=form.password.data).decode('UTF-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. LogIn now.', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'You have been Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(f'Login Failed. Please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['POST', 'GET'])
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
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_image = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html', title='User Account', profile_image=profile_image, form=form)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("user_posts.html", posts=posts, user=user)


@users.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(f'An email with instructions to reset password has been sent to your registered email.', 'info')
        return redirect(url_for('users.login'))
    return render_template("reset_request.html", title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash(f'Token invalid or expired!!!', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(password=form.password.data).decode('UTF-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!!! LogIn now.', 'success')
        return redirect(url_for('users.login'))
    return render_template("reset_token.html", title='Reset Password', form=form)
