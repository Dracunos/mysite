import os
from flask import Flask, render_template, redirect, request
from flask_wtf import Form
from wtforms import StringField, RadioField, validators
from random import randint
from mods import journeygame
from config import basedir

app = Flask(__name__)
app.config.from_object('config')


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


if __name__ == '__main__':
    app.run(debug=True)
