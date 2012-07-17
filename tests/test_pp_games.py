import requests
import unittest
import uuid
import json
from utils import BASE, create_user, get_new_user_id_auth


class TestUserContestGames(unittest.TestCase):
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
        r = requests.post(BASE + "/users/%s/contests" % self.id, data={"data": json.dumps({"name": "boo", "type":"manyranked"})}, auth=self.auth)
        self.contest_id = r.json["data"]["id"]

    def add_players(self, contest_id):
        # Now create players
        players = []
        for i in range(10):
            r = requests.post(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), data={"name": "boo"}, auth=self.auth)
            players.append(r.json["data"]["id"])
        return players

    def test_list(self):
        data = requests.get(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert("games" in data)
        assert(len(data["games"]) == 0)
        players = self.add_players(self.contest_id)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), 
                          data={"date": "2012-6-12", "ranking": json.dumps(players)}, 
                          auth=self.auth)
        data = requests.get(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert("games" in data)
        assert(len(data["games"]) == 1)

    def test_create(self):
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), auth=self.auth)
        assert(r.status_code == 400)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), data={"data": json.dumps({"date": "2012-6-12"})}, auth=self.auth)
        assert(r.status_code == 400)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), data={"data": json.dumps({"date": "2012-6-12"})}, auth=self.auth)
        print r.text

    def test_get(self):
        r = requests.get(BASE + "/users/%s/contests/%s/games/%s" % (self.id, self.contest_id, 23423), auth=self.auth)
        assert(r.status_code == 404)
        players = self.add_players(self.contest_id)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), 
                          data={"data": json.dumps({"date": "2012-6-12", "ranking": json.dumps(players)})}, 
                          auth=self.auth)
        game_id = r.json["data"]["id"]
        r = requests.get(BASE + "/users/%s/contests/%s/games/%s" % (self.id, self.contest_id, game_id), auth=self.auth)
        assert(r.status_code == 200)
        assert("game" in r.json["data"])
        assert("contest_id" in r.json["data"]["game"])
        assert("ranking" in r.json["data"]["game"])
        assert("date" in r.json["data"]["game"])

    def test_delete(self):
        players = self.add_players(self.contest_id)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), 
                          data={"date": "2012-6-12", "ranking": json.dumps(players)}, 
                          auth=self.auth)
        game_id = r.json["data"]["id"]
        r = requests.get(BASE + "/users/%s/contests/%s/games/%s" % (self.id, self.contest_id, game_id), auth=self.auth)
        assert(r.status_code == 200)
        data = requests.get(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert(len(data["games"]) == 1)
        r = requests.delete(BASE + "/users/%s/contests/%s/games/%s" % (self.id, self.contest_id, game_id), auth=self.auth)
        r = requests.get(BASE + "/users/%s/contests/%s/games/%s" % (self.id, self.contest_id, game_id), auth=self.auth)
        assert(r.status_code == 404)
        data = requests.get(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert(len(data["games"]) == 0)
        id, auth = get_new_user_id_auth()
        players = self.add_players(self.contest_id)
        r = requests.post(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), 
                          data={"date": "2012-6-12", "ranking": json.dumps(players)}, 
                          auth=self.auth)
        game_id = r.json["data"]["id"]
        r = requests.delete(BASE + "/users/%s/contests/%s/games/%s" % (self.id, self.contest_id, game_id), auth=auth)
        assert(r.status_code == 403)
        r = requests.get(BASE + "/users/%s/contests/%s/games/%s" % (self.id, self.contest_id, game_id), auth=self.auth)
        assert(r.status_code == 200)
        data = requests.get(BASE + "/users/%s/contests/%s/games" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert(len(data["games"]) == 1)


if __name__ == "__main__":
    unittest.main()
