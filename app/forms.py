from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, SubmitField,
                     TextAreaField)
from wtforms.validators import (DataRequired, ValidationError, Email, EqualTo,
                                Length)
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    login = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email ID', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    conf_password = PasswordField('Confirm Password',
                                  validators=[DataRequired(),
                                              EqualTo('password')])
    remember_me = BooleanField('Remember Me')
    signup = SubmitField('Sign Up')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username ==
                                                       username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email ==
                                                       email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About Me', validators=[Length(min=0, max=140)])
    update = SubmitField('Update')
    
    def __init__(self, orig_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orig_username = orig_username

    def validate_username(self, username):
        if username.data != self.orig_username:
            user = db.session.scalar(sa.select(User).where(User.username == self.username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(),
                                                      Length(min=1, max=140)])
    submit = SubmitField('Post')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email ID', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    conf_password = PasswordField('Confirm Password',
                                  validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
