from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from blogger.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose another or LogIn.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists. Please choose another or LogIn.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_pic = FileField('Update Profile Pic', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('User already exists. Please choose another or LogIn.')

    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exists. Please choose another or LogIn.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email does not exist. Please change email or Register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
