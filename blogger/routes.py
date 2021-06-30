from flask import render_template, url_for, flash, redirect
from blogger import app
from blogger.forms import RegistrationForm, LoginForm
# from blogger.models import User, Post


posts = [
    {
        'author': 'Nitesh Rathee',
        'title': 'Blog Post',
        'content': 'This is the first post on this blog.',
        'created_on': 'June 28, 2021'
    },
    {
        'author': 'Mrinal Rawat',
        'title': 'Blog Post 2',
        'content': 'This is the first post on this blog by Mrinal.',
        'created_on': 'June 29, 2021'
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html", posts=posts)


@app.route('/about')
def about():
    return render_template("about.html", title='About Page')


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}! successfully', 'success')
        return redirect(url_for('about'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@demo.com" and form.password.data == "password":
            flash(f'You have been Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Login Unsuccessful. Please check your email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)
