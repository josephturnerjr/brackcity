import requests
import uuid
import json

BASE = "http://127.0.0.1:5000"

def get_admin_auth():
    r = requests.post(BASE + "/login", data={"data": '{"username": "turnerj9", "password": "Pass1234"}'})
    return (r.json["data"]["session_token"], 'foo')

def create_user(name, username, password):
    auth = get_admin_auth()
    r = requests.post(BASE + "/users", data={"data": json.dumps({"name": name, "username": username, "password": password})}, auth=auth)
    return r.json["data"]

def get_new_user_id_auth():
    username = uuid.uuid4().hex
    password = uuid.uuid4().hex
    name = "Joseph Tester"
    nu_data = {"name": name,
               "username": username,
               "password": password}
    id = create_user(**nu_data)["id"]
    good = {"data": json.dumps({"username": username, "password": password})}
    r = requests.post(BASE + "/login", data=good)
    auth = (r.json["data"]["session_token"], "foo")
    return (id, auth)

if __name__ == "__main__":
    get_admin_auth()
