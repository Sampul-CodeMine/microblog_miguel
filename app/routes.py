from flask import (render_template, redirect, flash, url_for)
from app import app
from app.forms import LoginForm

@app.route('/', strict_slashes=False)
@app.route('/index', strict_slashes=False)
def index():
    user = {'username': 'Dukeson'}
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
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/signin', strict_slashes=False, methods=['GET', 'POST'])
def signin():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash(f'Login was successful for user {login_form.username.data},'
              f' remember_me={login_form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', form=login_form, title="Login")
