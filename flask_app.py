import os
from random import randint
from flask import (Flask, render_template, redirect, request, url_for, g,
                   flash)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, login_required, login_user,
                         current_user, logout_user)
from flask_wtf import Form
from wtforms import StringField, RadioField, validators, BooleanField
from mods import journeygame
from config import basedir

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

import models


@app.route('/')
def index():
    x = open(os.path.join(basedir, 'textdata/post.txt'), 'r')
    filer = x.readlines()
    x.close()
    return render_template('index.html', filer=filer)


@app.route('/form', methods=['GET', 'POST'])
def myform():
    form = MyForm()
    if form.validate_on_submit():
        poster = form.poster.data
        posted = form.posted.data
        x = open(os.path.join(basedir, 'textdata/post.txt'), 'a')
        x.write('\n' + poster + ': ' + posted)
        x.close()
        return redirect(url_for('index'))
    else:
        flash_errors(form)
    return render_template('myform.html', form=form, ttl='New Post')


@app.route('/test')
def test():
    tt = '<a href="https://www.google.com">Goog</a>'
    return """This is my test page.
    <br> Link from var: {}
    """.format(tt)


@app.route('/journey')
def journey():
    page = request.args.get('pg', '1')
    textlist = journeygame.pages[int(page)]['text']
    links = journeygame.pages[int(page)]['links']
    if page == '1':
        stats = [randint(3, 18), randint(3, 18), randint(3, 18)]
        return render_template('journey.html', ttl="Journey of Distangibility",
                               story=textlist, links=links, stats=stats)
    return render_template('journey.html', ttl="Journey of Distangibility",
                           story=textlist, links=links)


@app.route('/hangman', methods=['GET', 'POST'])
def hangedman():
    form = HMForm()
    formnew = NHMForm()

    x = open(os.path.join(basedir, 'textdata/hmdata.txt'), 'r')
    hmdata = x.readlines()
    x.close()
    x = open(os.path.join(basedir, 'textdata/hmwords.txt'), 'r')
    wordlist = x.readlines()
    x.close()
    category = None
    for i in wordlist:
        for q in i.split():
            if hmdata[0][0:-1] == q:
                category = i.split()[0].title()
    if len(hmdata) == 1:
        hmdata.append('')

    tried = ' '.join(hmdata[1])
    word = ''

    won = True
    for i in hmdata[0][0:-1]:
        if i in hmdata[1]:
            word += i
        else:
            word += ' _ '
            won = False

    missed = 0
    lost = False
    for i in hmdata[1]:
        if i not in hmdata[0][0:-1]:
            missed += 1
    if missed == 6:
        lost = True

    if formnew.validate_on_submit() and request.form['btn'] == 'New Game':
        hmwords = open(os.path.join(basedir, 'textdata/hmwords.txt'), 'r')
        wordlist = hmwords.readlines()
        hmwords.close()
        for i in wordlist:
            l = i.split()
            if formnew.gametype.data == l[0]:
                newgame = l[randint(1, len(l)-1)]
                x = open(os.path.join(basedir, 'textdata/hmdata.txt'), 'w+')
                x.write(newgame + '\n')
                x.close()
                return redirect('/hangman')
        return 'Error, can\'t find ' + formnew.gametype.data
    else:
        flash_errors(form)
    if won:
        return render_template('hmend.html', word=hmdata[0][0:-1], won=won,
                               formnew=formnew, ttl='Hangman')
    if lost:
        return render_template('hmend.html', word=hmdata[0][0:-1], won=won,
                               formnew=formnew, ttl='Hangman')

    if form.validate_on_submit() and request.form['btn'] == 'Submit':
        hminput = form.hminput.data.lower()
        if hminput not in 'abcdefghijklmnopqrstuvwxyz':
            return render_template('hangedman.html', form=form, word=word,
                                   tried=tried, missed=missed, numin=True,
                                   category=category, ttl='Hangman')
        if hminput in hmdata[1]:
            return render_template('hangedman.html', form=form, word=word,
                                   tried=tried, missed=missed,
                                   alreadypick=True, category=category,
                                   ttl='Hangman')
        x = open(os.path.join(basedir, 'textdata/hmdata.txt'), 'a')
        hminput = str(hminput)
        x.write(hminput)
        x.close()
        return redirect('/hangman')
    else:
        flash_errors(form)

    return render_template('hangedman.html', form=form, word=word, tried=tried,
                           missed=missed, category=category, ttl='Hangman')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.title()
        user = models.User.query.filter_by(username=username).first()
        if user is None:  # Username is not in database
            flash('Username not found. Please register.')
            return redirect(url_for('registration'))
        if user.check_password(form.password.data):  # password check
            remember_me = form.remember_me.data
            login_user(user, remember=remember_me)
            flash('Welcome, ' + user.username)
            return redirect(url_for('index'))
        else:
            flash('Incorrect password.')
            return redirect(url_for('login'))
    else:
        flash_errors(form)
        print '-------------------------flashing errors'
    return render_template('login.html', form=form, ttl='Login')


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def registration():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.title()
        if models.User.query.filter_by(username=username).first() is not None:
            flash('Username is already taken.')
            return redirect(url_for('registration'))
        password = form.password.data
        user = models.User(username, password)
        db.session.add(user)
        db.session.commit()
        flash('Registered, please log in.')
        return redirect(url_for('login'))
    else:
        flash_errors(form)
    return render_template('register.html', form=form, ttl='Registration')


@lm.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))


@app.route('/membersarea')
@login_required
def members_area():
    return render_template('membersarea.html', ttl='Members Area')


class LoginForm(Form):
    username = StringField('username', validators=[validators.DataRequired(
        message='Username required.'
    )])
    password = StringField('password', validators=[validators.DataRequired(
        message='Password required.'
    )])
    remember_me = BooleanField('remember_me', default=False)


class RegistrationForm(Form):
    username = StringField('username', validators=[validators.DataRequired(
        message='Username required.'
    )])
    password = StringField('password', validators=[validators.DataRequired(
        message='Password required.'
    )])


@app.before_request
def before_request():
    g.user = current_user


class MyForm(Form):
    poster = StringField('poster')
    posted = StringField('posted')


class HMForm(Form):
    hminput = StringField('hminput', [validators.Length(min=1, max=1)])


class NHMForm(Form):
    gametype = RadioField(
        'gametype', choices=[('animals', 'Animals (easy)'),
                             ('food', 'Food (easy)'),
                             ('technology', 'Technology'),
                             ('countries', 'Countries')],
        default='animals')


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        print '------------------for each form.errors'
        for error in errors:
            print '-----------------for each error'
            flash(error)


if __name__ == '__main__':
    app.run(debug=True)
