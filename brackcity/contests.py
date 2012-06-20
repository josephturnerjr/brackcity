from flask import g


class GameValidationError(Exception):
    pass


class Contest(object):
    def __init__(self, user_id, name, contest_type, contest_id):
        self.name = name
        self.user_id = user_id 
        self.contest_type = contest_type
        self.db_id = contest_id

    def validate(self, date, **kwargs):
        try:
            parsed_date = datetime.date(*map(int, date.split("-")))
        except TypeError:
            return json_response(400,
                                 "Date must be in YYYY-MM-DD format")
        except ValueError, e:
            return json_response(400,
                                 "Couldn't parse a valid date from %s" % date)


class PingPong(Contest):
    def validate(self, **kwargs):
        Contest.validate(self, **kwargs)


class ManyPlayersRanked(Contest):
    def validate(self, ranking, **kwargs):
        Contest.validate(self, **kwargs)
        try:
            ranking = json.loads(ranking)
        except ValueError:
            return json_response(400,
                                 "Rankings must be a list of player ids in decreasing order of score")
        if not isinstance(ranking, list):
            return json_response(400,
                                 "Rankings must be a list of player ids in decreasing order of score")
        if len(ranking) < 2:
            return json_response(400,

                                 "Games must have two or more players")


CONTEST_FACTORIES = {
                        "pingpong": PingPong,
                        "manyranked": ManyPlayersRanked
                    }


def create_contest(user_id, name, contest_type):
    cur = g.db.cursor()
    cur.execute("""insert into contests (user_id, name, type)
                                  values (?, ?, ?)""",
                 (user_id, name, contest_type))
    g.db.commit()
    contest_id = cur.lastrowid
    return CONTEST_FACTORIES[contest_type](user_id, name, contest_type, contest_id)
