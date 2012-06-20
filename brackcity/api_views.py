from brackcity import app
from flask import (request, g, jsonify, json)
import uuid
import datetime
from auth import (requires_auth, check_session_auth, check_admin,
                  hash_pw, check_pw)
from db_functions import connect_db, query_db
from contests import create_contest


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


def json_response(status=200, message="OK.", data=None):
    if data is not None:
        resp = jsonify(status=status, message=message, data=data)
    else:
        resp = jsonify(status=status, message=message)
    resp.status_code = status
    return resp


@app.route('/login', methods=['POST'])
def login():
    try:
        username = str(request.form['username'])
        password = str(request.form['password'])
    except KeyError, e:
        return json_response(400, "Required argument %s not found" % e.message)
    q = query_db('select id, name, pw_hash from users where username=?',
                 (username,),
                 one=True)
    if q:
        if check_pw(password, q['pw_hash']):
            is_admin = False
            admin_q = query_db('select id from admins where user_id=?',
                         (q["id"],),
                         one=True)
            is_admin = bool(admin_q)
            session_token = uuid.uuid4().hex
            g.db.execute("""insert into sessions (user_id, session_id,
                                                  creation_date, is_admin)
                                          values (?, ?, ?, ?)""",
                         (q["id"], session_token,
                          datetime.datetime.today(), is_admin))
            g.db.commit()
            return json_response(data={"session_token": session_token})
    return json_response(401, "Authorization required.")


# List contests
@app.route('/contests', methods=['GET'])
@requires_auth
def contests():
    contests = query_db('select id, user_id, name from contests')
    return json_response(data={"contests": contests})


@app.route('/contests/<contest_id>', methods=['GET'])
@requires_auth
def contest(contest_id):
    contest = query_db('select name, id, user_id from contests where id=?',
                 (contest_id,), one=True)
    if not contest:
        return json_response(404, "No such contest")
    return json_response(data={"contest": contest})


@app.route('/users', methods=['POST'])
@requires_auth
def create_user():
    check_admin()
    try:
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
            cur = g.db.cursor()
            cur.execute("""insert into users (name, username, pw_hash)
                                       values (?, ?, ?)""",
                         (name, username, password))
            g.db.commit()
            user_id = cur.lastrowid
            return json_response(data={"id": user_id})
    except KeyError, e:
        return json_response(400,
                             "Required argument %s not found" % e.message)


# List users
@app.route('/users', methods=['GET', 'POST'])
def users():
    users = query_db('select id, username from users')
    return json_response(data={"users": users})


# Get user
@app.route('/users/<int:user_id>', methods=['GET'])
@requires_auth
def user(user_id):
    user = query_db('select id, name, username from users where id=?',
                    (user_id,), one=True)
    if not user:
        return json_response(404, "No such user")
    return json_response(data={"user": user})


# List and create contests
@app.route('/users/<int:user_id>/contests', methods=['GET', 'POST'])
@requires_auth
def user_contests(user_id):
    user = query_db('select id from users where id=?',
                    (user_id,), one=True)
    if not user:
        return json_response(404, 'No such user')
    if request.method == 'POST':
        check_session_auth(user_id)
        try:
            name = str(request.form['name'])
            c_type = str(request.form['type'])
            contest = create_contest(user_id, name, c_type)
#            cur = g.db.cursor()
#            cur.execute("""insert into contests (user_id, name, type)
#                                          values (?, ?, ?)""",
#                         (user_id, name, c_type))
#            g.db.commit()
#            contest_id = cur.lastrowid
            return json_response(data={"id": contest.db_id})
        except KeyError, e:
            return json_response(400,
                                 "Required argument %s not found" % e.message)
    else:
        contests = query_db('select id, name from contests where user_id=?',
                            (user_id,))
        return json_response(data={"contests": contests})



# Get, update, and delete a contest
@app.route('/users/<int:user_id>/contests/<int:contest_id>',
           methods=['GET', 'PUT', 'DELETE'])
@requires_auth
def user_contest(user_id, contest_id):
    contest = query_db("""select contests.name, contests.id, contests.user_id
                                 from users, contests
                                          where (users.id=contests.user_id and
                                                 users.id=? and
                                                 contests.id=?)""",
                    (user_id, contest_id), one=True)
    if not contest:
        return json_response(404, 'No such contest')
    if request.method == 'PUT':
        check_session_auth(user_id)
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
        check_session_auth(user_id)
        g.db.execute("""delete from contests where id=?""", (contest_id,))
        g.db.commit()
        return json_response()
    else:
        return json_response(data={"contest": contest})


# List and add participants
@app.route('/users/<int:user_id>/contests/<int:contest_id>/players',
           methods=['POST', 'GET'])
@requires_auth
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
        check_session_auth(user_id)
        try:
            name = request.form['name']
            player_user_id = None  # int(request.form['player_id'])
            cur = g.db.cursor()
            cur.execute("""insert into players (contest_id, name, user_id)
                                        values (?, ?, ?)""",
                         (contest["id"], name, player_user_id))
            g.db.commit()
            player_id = cur.lastrowid
            return json_response(data={"id": player_id})
        except KeyError, e:
            return json_response(400,
                                 "Required argument %s not found" % e.message)
    else:
        players = query_db("""select id, name, user_id from players
                                                       where contest_id=?""",
                           (contest_id,))
        return json_response(data={"players": players})


# Get, update, and delete a contest
@app.route('/users/<int:user_id>/contests/<int:contest_id>/players/<int:player_id>',
           methods=['GET', 'PUT', 'DELETE'])
@requires_auth
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
        check_session_auth(user_id)
        try:
            name = str(request.form['name'])
            player_user_id = None  # int(request.form['player_id'])
            g.db.execute("""update players set name=?, user_id=?
                                            where id=?""",
                         (name, player_user_id, player_id))
            g.db.commit()
            return json_response()
        except KeyError, e:
            return json_response(400,
                                 "Required argument %s not found" % e.message)
    elif request.method == 'DELETE':
        check_session_auth(user_id)
        g.db.execute("""delete from players where id=?""", (player_id,))
        g.db.commit()
        return json_response()
    else:
        return json_response(data={"player": player})


# List and add games
@app.route('/users/<int:user_id>/contests/<int:contest_id>/games',
           methods=['POST', 'GET'])
@requires_auth
def user_contest_games(user_id, contest_id):
    contest = query_db("""select contests.name, contests.id, contests.user_id
                                          from users, contests
                                          where (users.id=contests.user_id and
                                                 users.id=? and
                                                 contests.id=?)""",
                       (user_id, contest_id), one=True)
    if not contest:
        return json_response(404, 'No such contest')
    if request.method == 'POST':
        check_session_auth(user_id)
        try:
            date = request.form['date']
            try:
                parsed_date = datetime.date(*map(int, date.split("-")))
            except TypeError:
                return json_response(400,
                                     "Date must be in YYYY-MM-DD format")
            except ValueError, e:
                return json_response(400,
                                     "Couldn't parse a valid date from %s" % date)
            try:
                ranking = json.loads(request.form['ranking'])
            except ValueError:
                return json_response(400,
                                     "Rankings must be a list of player ids in decreasing order of score")
            if not isinstance(ranking, list):
                return json_response(400,
                                     "Rankings must be a list of player ids in decreasing order of score")
            if len(ranking) < 2:
                return json_response(400,
                                     "Games must have two or more players")
            players = query_db("""select id
                                   from players
                                   where id in (%s) and
                                   contest_id = ?""" % (",".join('?' * len(ranking)),),
                               ranking + [contest_id])
            if len(players) != len(ranking):
                return json_response(400,
                                     'Rankings must be for contest players')
            cur = g.db.cursor()
            cur.execute("""insert into games (date, contest_id)
                                        values (?, ?)""",
                         (parsed_date, contest_id))
            game_id = cur.lastrowid
            for i, player in enumerate(ranking):
                cur.execute("""insert into scores (game_id, player_id, score)
                                            values (?, ?, ?)""",
                             (game_id, player, float(len(ranking) - i) / len(ranking)))
            g.db.commit()
            return json_response(data={"id": game_id})
        except KeyError, e:
            return json_response(400,
                                 "Required argument %s not found" % e.message)
    else:
        games = query_db("""select id, date from games
                               where contest_id=?""", (contest_id,))
        return json_response(data={"games": games})


# Get, delete a game
@app.route('/users/<int:user_id>/contests/<int:contest_id>/games/<int:game_id>',
           methods=['GET', 'DELETE'])
@requires_auth
def user_contest_game(user_id, contest_id, game_id):
    game = query_db("""select games.date, games.contest_id
                          from games, users, contests
                          where (users.id=contests.user_id and
                                 games.contest_id=contests.id and
                                 users.id=? and
                                 contests.id=? and
                                 games.id=?)""",
                    (user_id, contest_id, game_id), one=True)
    if not game:
        return json_response(404, 'No such game')
    if request.method == 'DELETE':
        check_session_auth(user_id)
        g.db.execute("""delete from games where id=?""", (game_id,))
        g.db.execute("""delete from scores where game_id=?""", (game_id,))
        g.db.commit()
        return json_response()
    else:
        scores = query_db("""select player_id, score
                                from scores
                                where game_id=?""",
                          (game_id,))
        ordered = sorted(scores, key=lambda x: x["score"], reverse=True)
        ranking = map(lambda x: int(x["player_id"]), ordered)
        game["ranking"] = ranking
        return json_response(data={"game": game})


'''
# Get the current scoreboard
@app.route('/contests/<int:constest_id>/scoreboard', methods=['POST', 'GET', 'PUT', 'DELETE'])
'''

if __name__ == "__main__":
    app.run(debug=True, port=3456)
