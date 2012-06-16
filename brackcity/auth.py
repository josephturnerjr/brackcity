from flask import (request, g, abort, Response)
from passlib.hash import sha256_crypt
from functools import wraps
from db_functions import query_db


def check_auth(username, password):
    q = query_db('select user_id, is_admin from sessions where session_id=?',
                 (username,),
                 one=True)
    if q:
        g.auth_user_id = q["user_id"]
        g.is_user_admin = q["is_admin"]
        return True
    else:
        return False


def authenticate():
    return Response('Login required.', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def check_session_auth(user_id):
    if user_id != g.auth_user_id:
        abort(403)


def check_admin():
    if not g.is_user_admin:
        abort(403)


def hash_pw(password):
    return sha256_crypt.encrypt(password)


def check_pw(password, h):
    return sha256_crypt.verify(password, h)
