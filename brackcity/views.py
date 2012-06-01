from brackcity import app
from flask import request, redirect, url_for, render_template, g, session
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
    q = query_db('select name, pw_hash from users where username=?',
                 (username,),
                 one=True)
    if q:
        if check_pw(password, q['pw_hash']):
            session['logged_in'] = True
            session['name'] = q['name']
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


@app.route('/game', methods=['POST', 'GET'])
def add_game():
    if request.method == 'POST':
        with open('games.json', 'r') as f:
            obj = json.loads(f.read())
        if request.form["winner"] != request.form["loser"]:
            obj["games"].append([request.form["winner"],
                                 request.form["loser"]])
        with open('games.json', 'w') as f:
            obj = f.write(json.dumps(obj))
        return redirect(url_for('main'))
    else:
        with open('players.json', 'r') as f:
            obj = json.loads(f.read())
        players_options = "".join(["<option value='%s'>%s</option>" % (name, name) for name in obj["players"]])
        return """<form action='/game' method='post'>
                  <label>Winner</label>
                  <select name='winner'>%s</select>
                  <label>Loser</label>
                  <select name='loser'>%s</select>
                  <input type='submit' value='Add game'>
                  </form>""" % (players_options, players_options)

if __name__ == "__main__":
    app.run(debug=True, port=3456)
