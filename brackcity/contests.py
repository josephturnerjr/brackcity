from flask import g, json
from db_functions import query_db
import datetime


class GameValidationError(Exception):
    pass


class ContestError(Exception):
    pass


class Contest(object):
    _SCHEMA = {"date": "2012-7-16"}

    def __init__(self, user_id, name, contest_type, contest_id):
        self.name = name
        self.user_id = user_id
        self.contest_type = contest_type
        self.contest_id = contest_id

    def get_game_schema(self):
        raise NotImplementedError()

    def create_game(self, cur, scores, **kwargs):
        try:
            date = kwargs["date"]
            parsed_date = datetime.date(*map(int, date.split("-")))
        except TypeError:
            raise GameValidationError("Date must be in YYYY-MM-DD format")
        except ValueError:
            raise GameValidationError("Couldn't parse a valid date from %s" % date)
        except KeyError, e:
            raise GameValidationError("Required argument %s not found" % e.message)
        cur.execute("""insert into games (date, contest_id, json_scores)
                                    values (?, ?, ?)""",
                     (parsed_date, self.contest_id, scores))
        g.db.commit()
        return cur.lastrowid


class PingPong(Contest):
    _SCHEMA = dict(Contest._SCHEMA)
    _SCHEMA.update({"players": [1, 2], "games_played": 3, "game_scores": [[11, 9], [19, 21], [11, 2]]})
    GAME_SCHEMA = json.dumps(_SCHEMA)

    def get_game_schema(self):
        return self.GAME_SCHEMA

    def create_game(self, **kwargs):
        cur = g.db.cursor()
        try:
            players = kwargs["players"]
            scores = kwargs["game_scores"]
        except ValueError:
            raise GameValidationError("Game must be a valid JSON object")
        except KeyError, e:
            raise GameValidationError("Required argument %s not found" % e.message)
        if len(players) != 2:
            raise GameValidationError("This context is for singles ping pong, there must be 2 players")
        if not reduce(lambda x, y: x and y, map(lambda x: len(x) == 2, scores)):
            raise GameValidationError("Game scores must be lists of length 2")
        cplayers = query_db("""select id
                               from players
                               where id in (?,?) and
                               contest_id = ?""",  (players[0], players[1], self.contest_id))
        if len(cplayers) != 2:
            raise GameValidationError('Rankings must be for contest players')
        scores_json = json.dumps({"players": players, "scores": scores})
        game_id = Contest.create_game(self, cur, scores_json, **kwargs)
        return game_id


class ManyPlayersRanked(Contest):
    _SCHEMA = dict(Contest._SCHEMA)
    _SCHEMA.update({"ranking": [1]})
    GAME_SCHEMA = json.dumps(_SCHEMA)

    def get_game_schema(self):
        print ManyPlayersRanked.GAME_SCHEMA
        return ManyPlayersRanked.GAME_SCHEMA

    def create_game(self, **kwargs):
        cur = g.db.cursor()
        try:
            ranking = kwargs["ranking"]
        except ValueError:
            raise GameValidationError("Rankings must be a list of player ids in decreasing order of score")
        except KeyError, e:
            raise GameValidationError("Required argument %s not found" % e.message)
        if not isinstance(ranking, list):
            raise GameValidationError("Rankings must be a list of player ids in decreasing order of score")
        if len(ranking) < 2:
            raise GameValidationError("Games for this contest type must have two or more players")
        players = query_db("""select id
                               from players
                               where id in (%s) and
                               contest_id = ?""" % (",".join('?' * len(ranking)),),
                           ranking + [self.contest_id])
        if len(players) != len(ranking):
            raise GameValidationError('Rankings must be for contest players')
        scores_json = json.dumps({"ranking": ranking})
        game_id = Contest.create_game(self, cur, scores_json, **kwargs)
        return game_id


CONTEST_FACTORIES = {
                        "pingpong": PingPong,
                        "manyranked": ManyPlayersRanked
                    }


def create_contest(user_id, name, contest_type):
    if contest_type not in CONTEST_FACTORIES:
        raise ContestError("No such contest type")
    cur = g.db.cursor()
    cur.execute("""insert into contests (user_id, name, type)
                                  values (?, ?, ?)""",
                 (user_id, name, contest_type))
    g.db.commit()
    contest_id = cur.lastrowid
    return CONTEST_FACTORIES[contest_type](user_id, name,
                                           contest_type, contest_id)


def load_contest(user_id, contest_id):
    contest = query_db("""select contests.name, contests.id, contests.user_id,
                                 contests.type
                                          from users, contests
                                          where (users.id=contests.user_id and
                                                 users.id=? and
                                                 contests.id=?)""",
                       (user_id, contest_id), one=True)
    if contest:
        return CONTEST_FACTORIES[contest["type"]](user_id, contest["name"],
                                                  contest["type"], contest_id)
    return None
