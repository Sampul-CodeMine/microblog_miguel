from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import (StringField, PasswordField, BooleanField, SubmitField,
                     TextAreaField)
from wtforms.validators import (DataRequired, ValidationError, Email, EqualTo,
                                Length)
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    login = SubmitField(_l('Sign In'))


class RegisterForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email ID'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    conf_password = PasswordField(_l('Confirm Password'),
                                  validators=[DataRequired(),
                                              EqualTo('password')])
    signup = SubmitField(_l('Sign Up'))

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username ==
                                                       username.data))
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email ==
                                                       email.data))
        if user is not None:
            raise ValidationError(_l('Please use a different email address.'))


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About Me'), validators=[Length(min=0, max=140)])
    update = SubmitField(_l('Update'))
    
    def __init__(self, orig_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orig_username = orig_username

    def validate_username(self, username):
        if username.data != self.orig_username:
            user = db.session.scalar(sa.select(User).where(User.username == self.username.data))
            if user is not None:
                raise ValidationError(_l('Please use a different username.'))


class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired(),
                                                      Length(min=1, max=140)])
    submit = SubmitField(_l('Post'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email ID'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('New Password'), validators=[DataRequired()])
    conf_password = PasswordField(_l('Confirm Password'),
                                  validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Reset Password'))
