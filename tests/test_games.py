import requests
import unittest
import uuid
import json
from utils import BASE, create_user


class TestUserContestGames(unittest.TestCase):
    def setUp(self):
        self.username = uuid.uuid4().hex
        self.password = uuid.uuid4().hex
        self.name = "Joseph Tester"
        nu_data = {"name": self.name,
                   "username": self.username,
                   "password": self.password}
        self.id = create_user(**nu_data)["id"]
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
                          data={"date": "2012-16-12", "ranking": json.dumps([1, 2])}, 
                          auth=self.auth)
        assert(r.status_code == 400)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), 
                          data={"date": "bullshit", "ranking": json.dumps([1, 2])}, 
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
