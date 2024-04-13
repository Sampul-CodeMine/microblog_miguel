from flask import (render_template, redirect, flash, url_for, request)
from app.forms import LoginForm, RegisterForm, EditProfileForm
from flask_login import (current_user, login_user, logout_user,
                         login_required)
import sqlalchemy as sa
from app import app, db
from app.models import User
from urllib.parse import urlsplit
from datetime import datetime, timezone


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/', strict_slashes=False)
@app.route('/index', strict_slashes=False)
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Nigeria!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'I love Wrestlemania XL!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/signin', strict_slashes=False, methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == login_form.username.data))
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('signin'))
        login_user(user, remember=login_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        flash(f'Login was successful for user {login_form.username.data},'
              f' remember_me={login_form.remember_me.data}')
        return redirect(next_page)
    return render_template('login.html', form=login_form, title="Login")


@app.route('/signout', strict_slashes=False)
def signout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/signup', strict_slashes=False, methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    signup_form = RegisterForm()
    if signup_form.validate_on_submit():
        user = User(username=signup_form.username.data,
                    email=signup_form.email.data)
        user.set_password(signup_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your registration was successful. Login to your account.')
        return redirect(url_for('signin'))
    return render_template('register.html', form=signup_form,
                           title="Register")


@app.route('/user/<username>', strict_slashes=False)
@login_required
def profile(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {
            'author': user,
            'body': 'Beautiful day in Nigeria!'
        },
        {
            'author': user,
            'body': 'I love Wrestlemania XL!'
        }
    ]
    return render_template('user.html', title='Profile',
                           user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def edit_profile():
    user = current_user.username
    edit_form = EditProfileForm()
    if edit_form.validate_on_submit():
        current_user.username = edit_form.username.data
        current_user.about_me = edit_form.about_me.data
        db.session.commit()
        flash('Your profile was successfully updated.')
        return redirect(url_for('profile', username=user))
    elif request.method == 'GET':
        edit_form.username.data = current_user.username
        edit_form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Profile Update', form=edit_form)
