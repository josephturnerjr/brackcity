from brackcity import app
from flask import g
import sqlite3
from contextlib import closing


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        cur = db.cursor()
        with app.open_resource('schema.sql') as f:
            cur.executescript(f.read())
        # REMOVE ME
        cur.execute("""insert into users (name, username, pw_hash)
                                          values (?, ?, ?)""",
                            ('Joseph Turner',
                            'turnerj9',
                            '$5$rounds=80000$Ed98ValkoHY.Zjk9$W4SLg3m9dQ.RJq1Cu2QzdlO9noMoh2AwrOXtJISGCL0'))
        cur.execute("""insert into admins (user_id) values (?)""", 
                    (cur.lastrowid, ))
        db.commit()


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv
