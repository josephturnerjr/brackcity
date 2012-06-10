from brackcity import app
from flask import (request, redirect, url_for,
                   render_template, g, session, abort, jsonify)
import sqlite3
from contextlib import closing
from passlib.hash import sha256_crypt
import uuid


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


def json_response(status=200, message="OK.", data=None):
    if data is not None:
        resp = jsonify(status=status, message=message, data=data)
    else:
        resp = jsonify(status=status, message=message)
    resp.status_code = status
    return resp


@app.route('/login', methods=['POST'])
def login():
    username = str(request.form['username'])
    password = str(request.form['password'])
    q = query_db('select id, name, pw_hash from users where username=?',
                 (username,),
                 one=True)
    if q:
        if check_pw(password, q['pw_hash']):
            session_token = uuid.uuid4().hex
            return json_response(data=session_token)
    # If login fails, return 401
    json_response(401, "Authorization required.")


@app.route('/newuser', methods=['POST'])
def create_user():
    name = str(request.form['name'])
    username = str(request.form['username'])
    password = hash_pw(str(request.form['password']))
    # Check if the username exists
    q = query_db('select id from users where username=?',
                 (username,),
                 one=True)
    if q:
        return json_response(409, "User already exists")
    else:
        g.db.execute("""insert into users (name, username, pw_hash)
                                   values (?, ?, ?)""",
                     (name, username, password))
        g.db.commit()
    return json_response()


# List contests
@app.route('/contests', methods=['GET'])
def contests():
    contests = query_db('select id, user_id, name from contests')
    return json_response(data=contests)

@app.route('/contests/<contest_id>', methods=['GET'])
def contest(contest_id):
    contest = query_db('select name, id, user_id from contests where id=?',
                 (contest_id,), one=True)
    if not contest:
        return json_response(404, "No such contest")
    return json_response(data=contest)


# List users
@app.route('/users', methods=['GET'])
def users():
    users = query_db('select id, username from users')
    return json_response(data=users)


# List users
@app.route('/users/<int:user_id>', methods=['GET'])
def user(user_id):
    user = query_db('select id, name, username from users where id=?', (user_id,))
    if not user:
        return json_response(404, "No such user")
    return json_response(data=user)


# List and create contests
@app.route('/users/<int:user_id>/contests', methods=['GET', 'POST'])
def user_contests(user_id):
    user = query_db('select id from users where id=?',
                    (user_id,), one=True)
    if not user:
        return json_response(404, 'No such user')
    if request.method == 'POST':
        # TODO check session id
        try:
            name = str(request.form['name'])
            # Ultimately can pull the user_id from the session
            g.db.execute("""insert into contests (user_id, name)
                                          values (?, ?)""",
                         (user_id, name))
            g.db.commit()
            return json_response()
        except KeyError, e:
            return json_response(400,
                                 "Required argument %s not found" % e.message)
    else:
        contests = query_db('select id, name from contests where user_id=?', (user_id,))
        return json_response(data=contests)


# Get, update, and delete a contest
@app.route('/users/<int:user_id>/contests/<int:contest_id>',
           methods=['GET', 'PUT', 'DELETE'])
def user_contest(user_id, contest_id):
    contest = query_db("""select contests.name, contests.id, contests.user_id from users, contests
                                          where (users.id=contests.user_id and
                                                 users.id=? and
                                                 contests.id=?)""",
                    (user_id, contest_id), one=True)
    if not contest:
        return json_response(404, 'No such contest')
    if request.method == 'PUT':
        try:
            name = str(request.form['name'])
            g.db.execute("""update contests set user_id=?, name=?
                                            where id=?""",
                         (user_id, name, contest_id))
            g.db.commit()
            return json_response()
        except KeyError, e:
            return json_response(400,
                                 "Required argument %s not found" % e.message)
    elif request.method == 'DELETE':
        g.db.execute("""delete from contests where id=?""", (contest_id,))
        g.db.commit()
        return json_response()
    else:
        return json_response(data=contest)

# List and add participants
@app.route('/users/<int:user_id>/contests/<int:contest_id>/players',
           methods=['POST', 'GET'])
def user_contest_players(user_id, contest_id):
    contest = query_db("""select contests.name, contests.id, contests.user_id
                                          from users, contests
                                          where (users.id=contests.user_id and
                                                 users.id=? and
                                                 contests.id=?)""",
                       (user_id, contest_id), one=True)
    if not contest:
        return json_response(404, 'No such contest')
    if request.method == 'POST':
        try:
            name = request.form['player_name']
            player_user_id = None  # int(request.form['player_id'])
            g.db.execute("""insert into players (contest_id, name, user_id)
                                        values (?, ?, ?)""",
                         (contest["id"], name, player_user_id))
            g.db.commit()
            return json_response()
        except KeyError, e:
            return json_response(400,
                                 "Required argument %s not found" % e.message)
    else:
        players = query_db("""select id, name, user_id from players
                                                       where contest_id=?""",
                           (contest_id,))
        return json_response(data=players)

# Get, update, and delete a contest
@app.route('/users/<int:user_id>/contests/<int:contest_id>/players/<int:player_id>',
           methods=['GET', 'PUT', 'DELETE'])
def user_contest_player(user_id, contest_id, player_id):
    player = query_db("""select players.name, players.id, players.user_id
                          from users, contests, players
                          where (users.id=contests.user_id and
                                 players.contest_id=contests.id and
                                 users.id=? and
                                 contests.id=? and
                                 players.id=?)""",
                    (user_id, contest_id, player_id), one=True)
    if not player:
        return json_response(404, 'No such player')
    if request.method == 'PUT':
        try:
            name = str(request.form['name'])
            player_user_id = None  # int(request.form['player_id'])
            g.db.execute("""update players set name=?, user_id=?
                                            where id=?""",
                         (name, player_user_id))
            g.db.commit()
            return json_response()
        except KeyError, e:
            return json_response(400,
                                 "Required argument %s not found" % e.message)
    elif request.method == 'DELETE':
        g.db.execute("""delete from players where id=?""", (player_id,))
        g.db.commit()
        return json_response()
    else:
        return json_response(data=player)
'''
# Get, update, and delete a participant
@app.route('/contests/<int:constest_id>/participants/<int:participant_id>', methods=['GET', 'PUT', 'DELETE'])
# List and add games 
@app.route('/contests/<int:constest_id>/games', methods=['POST', 'GET'])
# Get, update, and delete a game 
@app.route('/contests/<int:constest_id>/games/<int:game_id>', methods=['GET', 'PUT', 'DELETE'])
# Get the current ranking
@app.route('/contests/<int:constest_id>/ranking', methods=['POST', 'GET', 'PUT', 'DELETE'])
# Get the current scoreboard
@app.route('/contests/<int:constest_id>/scoreboard', methods=['POST', 'GET', 'PUT', 'DELETE'])

@app.route('/users')
@app.route('/users/<user_id>')
@app.route('/users/<user_id>/contests')





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
        player_user_id = None  # int(request.form['player_id'])
        g.db.execute("""insert into players (contest_id, name, user_id)
                                   values (?, ?, ?)""",
                     (contest_id, name, player_user_id))
        g.db.commit()
        return redirect(url_for('players', contest_id=contest_id))
    else:
        players = query_db('select id, name, user_id from players where contest_id=?',
                       (contest_id,))
        return render_template('players.html', contest=contest, players=players)


@app.route('/contest/<contest_id>/games', methods=['POST', 'GET'])
def games(contest_id):
    contest_id = int(contest_id)
    contest = query_db('select name, id, user_id from contests where id=?',
                 (contest_id,), one=True)
    if not contest:
        abort(404)
    if contest["user_id"] != session.get("user_id"):
        abort(401)
    if request.method == 'POST':
        winner = int(request.form['player_one'])
        loser = int(request.form['player_two'])
        date = request.form['game_date']
        # Add no-date error checking
        cur = g.db.cursor()
        cur.execute("""insert into games (contest_id, date)
                                   values (?, ?)""",
                     (contest_id, date))
        game_id = cur.lastrowid
        g.db.execute("""insert into scores (game_id, player_id, score)
                                    values (?, ?, ?)""",
                     (game_id, loser, 0.0))
        g.db.execute("""insert into scores (game_id, player_id, score)
                                    values (?, ?, ?)""",
                     (game_id, winner, 1.0))
        g.db.commit()
        return redirect(url_for('games', contest_id=contest_id))
    else:
        players = query_db("""select id, name, user_id from players
                                                       where contest_id=?""",
                       (contest_id,))
        games = query_db('select id, date from games where contest_id=?',
                         (contest_id,))
        return render_template('games.html', contest=contest, players=players,
                               games=games)


@app.route('/game', methods=['POST', 'GET'])
def add_game():
    return """<form action='/game' method='post'>
              <label>Winner</label>
              <select name='winner'>%s</select>
              <label>Loser</label>
              <select name='loser'>%s</select>
              <input type='submit' value='Add game'>
              </form>""" % ("1", "2")

'''
if __name__ == "__main__":
    app.run(debug=True, port=3456)
