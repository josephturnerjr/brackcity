import requests
import unittest
import uuid
import json

BASE = "http://127.0.0.1:5000"


class TestUsers(unittest.TestCase):
    def setUp(self):
        self.username = uuid.uuid4().hex
        self.password = uuid.uuid4().hex
        self.name = "Joseph Tester"
        nu_data = {"name": self.name,
                   "username": self.username,
                   "password": self.password}
        self.id = requests.post(BASE + "/users", data=nu_data).json["data"]["id"]
        good = {"username": self.username, "password": self.password}
        r = requests.post(BASE + "/login", data=good)
        self.auth = (r.json["data"]["session_token"], "foo")

    def test_user_creation(self):
        user_list = requests.get(BASE + "/users").json["data"]["users"]
        assert(self.username in map(lambda x: x["username"], user_list))
        assert(self.name == requests.get(BASE + "/users/%s" % self.id, auth=self.auth).json["data"]["user"]["name"])

    def test_login(self):
        good = {"username": self.username, "password": self.password}
        r = requests.post(BASE + "/login", data=good)
        assert(r.status_code == 200)
        assert(r.json["data"])
        wrong = {"username": self.username, "password": "self.password"}
        r = requests.post(BASE + "/login", data=wrong)
        assert(r.status_code == 401)
        wrong = {"username": self.username, "password": self.password[:10]}
        r = requests.post(BASE + "/login", data=wrong)
        assert(r.status_code == 401)
        wrong = {"username": self.username}
        r = requests.post(BASE + "/login", data=wrong)
        assert(r.status_code == 400)


class TestUserContests(unittest.TestCase):
    def setUp(self):
        self.username = uuid.uuid4().hex
        self.password = uuid.uuid4().hex
        self.name = "Joseph Tester"
        nu_data = {"name": self.name,
                   "username": self.username,
                   "password": self.password}
        requests.post(BASE + "/users", data=nu_data).json
        good = {"username": self.username, "password": self.password}
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

class TestUserContestGames(unittest.TestCase):
    def setUp(self):
        self.username = uuid.uuid4().hex
        self.password = uuid.uuid4().hex
        self.name = "Joseph Tester"
        nu_data = {"name": self.name,
                   "username": self.username,
                   "password": self.password}
        self.id = requests.post(BASE + "/users", data=nu_data).json["data"]["id"]
        good = {"username": self.username, "password": self.password}
        r = requests.post(BASE + "/login", data=good)
        self.auth = (r.json["data"]["session_token"], "foo")
        r = requests.post(BASE + "/users/%s/contests" % self.id, data={"name": "boo"}, auth=self.auth)
        self.contest_id = r.json["data"]["id"]

    def test_games(self):
        data = requests.get(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert("games" in data)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), auth=self.auth)
        assert(r.status_code == 400)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), data={"date": "2012-6-12"}, auth=self.auth)
        assert(r.status_code == 400)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), data={"date": "2012-6-12", "ranking": "Sdf"}, auth=self.auth)
        assert(r.status_code == 400)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), data={"date": "2012-6-12", "ranking": 123}, auth=self.auth)
        assert(r.status_code == 400)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), 
                          data={"date": "2012-6-12", "ranking": []}, 
                          auth=self.auth)
        assert(r.status_code == 400)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), 
                          data={"date": "2012-6-12", "ranking": json.dumps([1, 2])}, 
                          auth=self.auth)
        assert(r.status_code == 400)
        # Now create players
        players = []
        for i in range(10):
            r = requests.post(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), data={"name": "boo"}, auth=self.auth)
            players.append(r.json["data"]["id"])
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), 
                          data={"date": "2012-6-12", "ranking": json.dumps(players)}, 
                          auth=self.auth)
        assert(r.status_code == 200)
        assert("id" in r.json["data"])


if __name__ == "__main__":
    unittest.main()
