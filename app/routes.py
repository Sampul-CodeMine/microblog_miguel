from flask import (render_template, redirect, flash, url_for, request, g)
from app.forms import (LoginForm, RegisterForm, EditProfileForm,
                       EmptyForm, PostForm, ResetPasswordRequestForm,
                       ResetPasswordForm)
from flask_login import (current_user, login_user, logout_user,
                         login_required)
from flask_babel import _, get_locale
import sqlalchemy as sa
from app import app, db
from app.models import User, Post
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app.email import send_password_reset_email
from langdetect import detect, LangDetectException


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
    g.locale = str(get_locale())


@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
@app.route('/index', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post was submitted and it is now live!'), 'success')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/explore', strict_slashes=False)
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/signin', strict_slashes=False, methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == login_form.username.data))
        if user is None or not user.check_password(login_form.password.data):
            flash(_('Invalid username or password.'), 'danger')
            return redirect(url_for('signin'))
        login_user(user, remember=login_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        flash(f'Login attempt was successful.', 'success')
        return redirect(next_page)
    return render_template('login.html', form=login_form, title=_("Login"))


@app.route('/signout', strict_slashes=False)
def signout():
    logout_user()
    flash(_('You have successfully logged out.'), 'success')
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
        flash(_('Your registration was successful. Login to your account.'), 'success')
        return redirect(url_for('signin'))
    return render_template('register.html', form=signup_form,
                           title=_("Register"))


@app.route('/user/<username>', strict_slashes=False)
@login_required
def profile(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('profile', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('profile', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@app.route('/edit_profile', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def edit_profile():
    edit_form = EditProfileForm(current_user.username)
    if edit_form.validate_on_submit():
        current_user.username = edit_form.username.data
        current_user.about_me = edit_form.about_me.data
        db.session.commit()
        flash(_('Your profile was successfully updated.'),'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        edit_form.username.data = current_user.username
        edit_form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Profile Update'), form=edit_form)


@app.route('/follow/<username>', methods=['POST'], strict_slashes=False)
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found!', username=username), 'warning')
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot follow yourself.'), 'warning')
            return redirect(url_for('profile', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are now following %(username)s!', username=username), 'info')
        return redirect(url_for('profile', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'], strict_slashes=False)
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found!', username=username), 'warning')
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself.'), 'warning')
            return redirect(url_for('profile', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are no longer following %(username)s!', username=username), 'info')
        return redirect(url_for('profile', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/reset_password_request', methods=['GET', 'POST'],
           strict_slashes=False)
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data)
        )
        if user:
            send_password_reset_email(user)
        flash(_('Check you email for the instructions to reset your password.'), 'info')
        return redirect(url_for('signin'))
    return render_template('request_password_reset.html', title=_("Reset Password"), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'],
           strict_slashes=False)
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'), 'success')
        return redirect(url_for('signin'))
    return render_template('reset_password.html', form=form)
