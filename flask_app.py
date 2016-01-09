import os
from random import randint
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from flask_wtf import Form
from wtforms import StringField, RadioField, validators
import requests
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
        return redirect('/')
    return render_template('myform.html', form=form, ttl='New Post')


@app.route('/test')
def test():
    alex_id = '76561197975951347'
    key = '4B8D33CFBF8228FFA1F1435CABDA3818'
    r = requests.get("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/", params={'key':key, 'steamids':alex_id}).json()['response']['players'][0]
    alex_games = requests.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/", params={'key':key, 'steamid':alex_id}).json()['response']['games']
    total = sum([alex_games[i]['playtime_forever'] for i, v in enumerate(alex_games)]) / 60
    tt = '<a href="https://www.google.com">Goog</a>'
    return """This is my test page.
    <br> Link from var: {}
    <br>
    <br> Alex:
    <br>{}<br><img src={}>
    <br><br>
    Alex has wasted a total of {:,} recorded hours on steam games.. And that's just recorded.. What a jerk.<br>
    That's {:,} days of his life spent sitting at a chair playing video games! I'm sure the real number is well over {:,} days.
    """.format(tt, r['personaname'], r['avatarfull'], total, round(total / 24.0, 2), total // 12)


@app.route('/games')
def games():
    return render_template('games.html', ttl='Games')


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

    return render_template('hangedman.html', form=form, word=word, tried=tried,
                           missed=missed, category=category, ttl='Hangman')


@app.route('/hangmanjs', methods=['GET', 'POST'])
def hangmanjs():
    with open(os.path.join(basedir, 'textdata/hmwords.txt')) as x:
        wordlist = x.readlines()
    return render_template('hangmanjs.html', wordlist=wordlist, ttl='Hangman')


@app.route('/numbers', methods=['GET', 'POST'])
def numbers():
    x = open(os.path.join(basedir, 'textdata/nums.txt'), 'r')
    numdata = x.readlines()
    solved = True if numdata[0] == 'Solved\n' else False
    tries = int(numdata[1][:-1])
    answer = int(numdata[2])
    x.close()
    form = NumForm()
    newform = NewNumForm()
    if newform.validate_on_submit() and request.form['btn'] == 'New Game':
        randnum = randint(1, 100)
        x = open(os.path.join(basedir, 'textdata/nums.txt'), 'w')
        x.write('Unsolved\n0\n' + str(randnum))
        x.close()
        return redirect('/numbers')
    if form.validate_on_submit() and request.form['btn'] == 'Submit':
        num = form.num.data
        if num not in [str(i) for i in range(1, 101)]:
            return render_template('numbers.html', form=form, ttl='Numbers',
                                   tries = tries, wrongin = True)
        tries += 1
        if int(num) == answer:
            x = open(os.path.join(basedir, 'textdata/nums.txt'), 'w')
            x.write('Solved\n' + str(tries) + '\n' + str(answer))
            x.close()
            return render_template('numend.html', form=newform, ttl='Numbers',
                                   tries = tries, justsolved = True,
                                   answer = answer)
        if int(num) > answer:
            greater = False
        if int(num) < answer:
            greater = True
        x = open(os.path.join(basedir, 'textdata/nums.txt'), 'w')
        x.write('Unsolved\n' + str(tries) + '\n' + str(answer))
        x.close()
        form.num.data = None
        return render_template('numbers.html', form=form, ttl='Numbers',
                               tries = tries, greater = greater, num = num)

    if solved:
        return render_template('numend.html', form=newform, ttl='Numbers',
                               tries = tries, answer = answer)
    return render_template('numbers.html', form=form, ttl='Numbers',
                           tries = tries)


@app.route('/minesweeper')
def minesweeper():
    return render_template('minesweeper.html', ttl='Minesweeper')


@app.route('/membersarea')
@login_required
def members_area():
    return render_template('membersarea.html', ttl='Members Area')


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


class NumForm(Form):
    num = StringField('num')

class NewNumForm(Form):
    pass


if __name__ == '__main__':
    app.run(debug=True)
