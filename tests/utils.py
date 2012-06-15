import requests

BASE = "http://127.0.0.1:5000"

def get_admin_auth():
    r = requests.post(BASE + "/login", data={"username": 'turnerj9', "password": 'Pass1234'})
    return (r.json["data"]["session_token"], 'foo')

def create_user(name, username, password):
    auth = get_admin_auth()
    r = requests.post(BASE + "/users", data={"name": name, "username": username, "password": password}, auth=auth)
    return r.json["data"]

if __name__ == "__main__":
    get_admin_auth()
