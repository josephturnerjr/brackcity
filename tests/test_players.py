import requests
import unittest
import uuid
import json
from utils import BASE, create_user, get_new_user_id_auth



class TestUserContestPlayers(unittest.TestCase):
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
        r = requests.post(BASE + "/users/%s/contests" % self.id, data={"name": "boo", "type": "manyranked"}, auth=self.auth).json
        self.contest_id = r["data"]["id"]

    def test_list(self):
        r = requests.get(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert(len(r["players"]) == 0)
        r = requests.post(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), data={"name": "foo"}, auth=self.auth).json
        r = requests.get(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert(len(r["players"]) == 1)

    def test_create(self):
        # No name field
        r = requests.post(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), auth=self.auth)
        assert(r.status_code == 400)
        r = requests.post(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), data={"name": "foo"}, auth=self.auth)
        assert(r.status_code == 200)
        assert("id" in r.json["data"])
        pl_id = r.json["data"]["id"]
        r = requests.get(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert(len(r["players"]) == 1)
        assert(r["players"][0]["name"] == "foo")
        r = requests.get(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.status_code == 200)
        assert(r.json["data"]["player"]["name"] == "foo")
        # Test post from wrong user
        id, auth = get_new_user_id_auth()
        r = requests.post(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), data={"name": "bar"}, auth=auth)
        assert(r.status_code == 403)
        r = requests.get(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.status_code == 200)
        assert(r.json["data"]["player"]["name"] == "foo")

    def test_details(self):
        r = requests.get(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, 23498), auth=self.auth)
        assert(r.status_code == 404)
        r = requests.post(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), data={"name": "foo"}, auth=self.auth)
        pl_id = r.json["data"]["id"]
        r = requests.get(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.status_code == 200)
        assert("name" in r.json["data"]["player"])
        assert("id" in r.json["data"]["player"])
        # assert("user_id" in r.json["data"]["player"])
        assert(r.json["data"]["player"]["name"] == "foo")

    def test_delete(self):
        r = requests.delete(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, 23498), auth=self.auth)
        assert(r.status_code == 404)
        r = requests.post(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), data={"name": "foo"}, auth=self.auth)
        pl_id = r.json["data"]["id"]
        r = requests.get(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.status_code == 200)
        r = requests.get(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert(len(r["players"]) == 1)
        r = requests.delete(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.status_code == 200)
        r = requests.get(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.status_code == 404)
        r = requests.get(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert(len(r["players"]) == 0)
        # Test delete with wrong user
        id, auth = get_new_user_id_auth()
        r = requests.post(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), data={"name": "foo"}, auth=self.auth)
        pl_id = r.json["data"]["id"]
        r = requests.delete(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=auth)
        assert(r.status_code == 403)
        r = requests.get(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.status_code == 200)
        r = requests.get(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), auth=self.auth).json["data"]
        assert(len(r["players"]) == 1)

    def test_modify(self):
        r = requests.put(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, 23948), data={"name": "bar"}, auth=self.auth)
        assert(r.status_code == 404)
        r = requests.post(BASE + "/users/%s/contests/%s/players" % (self.id, self.contest_id), data={"name": "foo"}, auth=self.auth)
        pl_id = r.json["data"]["id"]
        r = requests.get(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.json["data"]["player"]["name"] == "foo")
        r = requests.put(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.status_code == 400)
        r = requests.put(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), data={"name": "bar"}, auth=self.auth)
        assert(r.status_code == 200)
        r = requests.get(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.json["data"]["player"]["name"] == "bar")
        # Test delete with wrong user
        id, auth = get_new_user_id_auth()
        r = requests.put(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), data={"name": "baz"}, auth=auth)
        assert(r.status_code == 403)
        r = requests.get(BASE + "/users/%s/contests/%s/players/%s" % (self.id, self.contest_id, pl_id), auth=self.auth)
        assert(r.json["data"]["player"]["name"] == "bar")


if __name__ == "__main__":
    unittest.main()
