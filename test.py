from contextlib import closing
import sqlite3
def connect_db():
    return sqlite3.connect('/tmp/testme.db')


def init_db():
    with closing(connect_db()) as db:
        with open('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

init_db()
db = connect_db()
db.execute("""insert into users (name, username, pw_hash)
                           values (?, ?, ?)""",
             ("a", "b", "c"))
db.commit()
db.execute("""insert into users (name, username, pw_hash)
                           values (?, ?, ?)""",
             ("a", "b", "c"))
db.commit()
