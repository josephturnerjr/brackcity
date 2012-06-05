from brackcity import app
from flask import (request, redirect, url_for,
                   render_template, g, session, abort)
import sqlite3
from contextlib import closing
from passlib.hash import sha256_crypt


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def hash_pw(password):
    return sha256_crypt.encrypt(password)


def check_pw(password, h):
    return sha256_crypt.verify(password, h)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.route('/')
def main():
    return render_template('base.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main'))


@app.route('/login', methods=['POST'])
def login():
    username = str(request.form['username'])
    password = str(request.form['password'])
    q = query_db('select id, name, pw_hash from users where username=?',
                 (username,),
                 one=True)
    if q:
        if check_pw(password, q['pw_hash']):
            session['logged_in'] = True
            session['user_name'] = q['name']
            session['user_id'] = q['id']
            return redirect(url_for('main'))
    return redirect(url_for('login'))


@app.route('/newuser', methods=['POST'])
def create_user():
    if request.method == 'POST':
        name = str(request.form['name'])
        username = str(request.form['username'])
        password = hash_pw(str(request.form['password']))
        # Check if the username exists
        q = query_db('select id from users where username=?',
                     (username,),
                     one=True)
        if not q:
            g.db.execute("""insert into users (name, username, pw_hash)
                                       values (?, ?, ?)""",
                         (name, username, password))
            g.db.commit()
        return redirect(url_for('main'))


@app.route('/user/<user_id>')
def user(user_id):
    user_id = int(user_id)
    user = query_db('select name, id from users where id=?',
                 (user_id,), one=True)
    if not user:
        abort(404)
    contests = query_db('select id, name from contests where user_id=?',
                 (user_id,))
    return render_template('user.html', user=user, contests=contests)


@app.route('/contest', methods=['POST', 'GET'])
def create_contest():
    if request.method == 'POST':
        name = str(request.form['contest_name'])
        user_id = int(request.form['user_id'])
        g.db.execute("""insert into contests (user_id, name)
                                   values (?, ?)""",
                     (user_id, name))
        g.db.commit()
        return redirect(url_for('user', user_id=user_id))
    else:
        return render_template('create_contest.html')


@app.route('/contest/<contest_id>', methods=['GET'])
def contest(contest_id):
    contest_id = int(contest_id)
    contest = query_db('select name, id, user_id from contests where id=?',
                 (contest_id,), one=True)
    if not contest:
        abort(404)
    players = query_db('select id, name, user_id from players where contest_id=?',
                       (contest_id,))
    games = query_db('select id, date from games where contest_id=?',
                     (contest_id,))
    return render_template('contest.html', contest=contest, players=players, games=games)


@app.route('/contest/<contest_id>/players', methods=['POST', 'GET'])
def players(contest_id):
    contest_id = int(contest_id)
    contest = query_db('select name, id, user_id from contests where id=?',
                 (contest_id,), one=True)
    if not contest:
        abort(404)
    if contest["user_id"] != session.get("user_id"):
        abort(401)
    if request.method == 'POST':
        name = request.form['player_name']
        player_user_id = None#int(request.form['player_id'])
        g.db.execute("""insert into players (contest_id, name, user_id)
                                   values (?, ?, ?)""",
                     (contest_id, name, player_user_id))
        g.db.commit()
        return redirect(url_for('players', contest_id=contest_id))
    else:
        players = query_db('select id, name, user_id from players where contest_id=?',
                       (contest_id,))
        return render_template('players.html', contest=contest, players=players)


@app.route('/game', methods=['POST', 'GET'])
def add_game():
    return """<form action='/game' method='post'>
              <label>Winner</label>
              <select name='winner'>%s</select>
              <label>Loser</label>
              <select name='loser'>%s</select>
              <input type='submit' value='Add game'>
              </form>""" % ("1", "2")

if __name__ == "__main__":
    app.run(debug=True, port=3456)
