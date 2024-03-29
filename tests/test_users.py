import requests
import unittest
import uuid
import json
from utils import BASE, create_user


class TestUserCreation(unittest.TestCase):
    def setUp(self):
        self.username = uuid.uuid4().hex
        self.password = uuid.uuid4().hex
        self.name = "Joseph Tester"
        nu_data = {"name": self.name,
                   "username": self.username,
                   "password": self.password}
        self.id = create_user(**nu_data)["id"]
        good = {"data": json.dumps({"username": self.username, "password": self.password})}
        r = requests.post(BASE + "/login", data=good)
        self.auth = (r.json["data"]["session_token"], "foo")

    def test_user_creation(self):
        user_list = requests.get(BASE + "/users").json["data"]["users"]
        assert(self.username in map(lambda x: x["username"], user_list))
        assert(self.name == requests.get(BASE + "/users/%s" % self.id, auth=self.auth).json["data"]["user"]["name"])

    def test_login(self):
        good = {"data": json.dumps({"username": self.username, "password": self.password})}
        r = requests.post(BASE + "/login", data=good)
        assert(r.status_code == 200)
        assert(r.json["data"])
        wrong= {"data": json.dumps({"username": self.username, "password": "self.password"})}
        r = requests.post(BASE + "/login", data=wrong)
        assert(r.status_code == 401)
        wrong = {"data": json.dumps({"username": self.username, "password": self.password[:10]})}
        r = requests.post(BASE + "/login", data=wrong)
        assert(r.status_code == 401)
        wrong = {"data": json.dumps({"username": self.username})}
        r = requests.post(BASE + "/login", data=wrong)
        assert(r.status_code == 400)

class TestUser(unittest.TestCase):
    def setUp(self):
        self.username = uuid.uuid4().hex
        self.password = uuid.uuid4().hex
        self.name = "Joseph Tester"
        nu_data = {"name": self.name,
                   "username": self.username,
                   "password": self.password}
        self.id = create_user(**nu_data)["id"]
        good = {"data": json.dumps({"username": self.username, "password": self.password})}
        r = requests.post(BASE + "/login", data=good)
        self.auth = (r.json["data"]["session_token"], "foo")

    def test_users(self):
        assert(self.username in map(lambda x: x["username"], requests.get(BASE + "/users", auth=self.auth).json["data"]["users"]))

    def test_user(self):
        users = requests.get(BASE + "/users").json["data"]["users"]
        my_id = filter(lambda x: x["username"] == self.username, users)[0]["id"]
        r = requests.get(BASE + "/users/%s" % (my_id), auth=self.auth)
        assert(r.status_code == 200)
        assert(r.json["data"]["user"]["name"] == self.name)
        r = requests.get(BASE + "/users/%s" % ("NOTANID"), auth=self.auth)
        assert(r.status_code == 404)
        r = requests.get(BASE + "/users/%s" % (0), auth=self.auth)
        assert(r.status_code == 404)


if __name__ == "__main__":
    unittest.main()
