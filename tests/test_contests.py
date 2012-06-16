import requests
import unittest
import uuid
import json
from utils import BASE, create_user



class TestUserContests(unittest.TestCase):
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

    def test_list(self):
        r = requests.get(BASE + "/users/%s/contests" % self.id, auth=self.auth).json
        assert("contests" in r["data"])
        assert(len(r["data"]["contests"]) == 0)
        r = requests.post(BASE + "/users/%s/contests" % self.id, data={"name": "boo"}, auth=self.auth)
        r = requests.get(BASE + "/users/%s/contests" % self.id, auth=self.auth).json
        assert("contests" in r["data"])
        assert(len(r["data"]["contests"]) == 1)
        
    def test_create(self):
        r = requests.post(BASE + "/users/%s/contests" % self.id)
        assert(r.status_code == 401)
        r = requests.post(BASE + "/users/%s/contests" % self.id, auth=self.auth)
        assert(r.status_code == 400)
        r = requests.post(BASE + "/users/%s/contests" % self.id, data={"name": "boo"}, auth=self.auth)
        assert(r.status_code == 200)
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex
        name = "Joseph Tester"
        nu_data = {"name": name,
                   "username": username,
                   "password": password}
        id = create_user(**nu_data)["id"]
        r = requests.post(BASE + "/users/%s/contests" % id, data={"name": "boo"}, auth=self.auth)
        assert(r.status_code == 403)

    def test_details(self):
        r = requests.post(BASE + "/users/%s/contests" % self.id, data={"name": "boo"}, auth=self.auth).json
        contest_id = r["data"]["id"]
        r = requests.get(BASE + "/users/%s/contests/%s" % (self.id, contest_id), auth=self.auth).json["data"]
        assert("user_id" in r["contest"])
        assert("name" in r["contest"])
        assert("id" in r["contest"])
        r = requests.get(BASE + "/users/%s/contests/%s" % (self.id, 9234923493), auth=self.auth)
        assert(r.status_code == 404)

    def test_delete(self):
        r = requests.post(BASE + "/users/%s/contests" % self.id, data={"name": "boo"}, auth=self.auth).json
        contest_id = r["data"]["id"]
        r = requests.get(BASE + "/users/%s/contests/%s" % (self.id, contest_id), auth=self.auth)
        assert(r.status_code == 200)
        r = requests.delete(BASE + "/users/%s/contests/%s" % (self.id, contest_id), auth=self.auth)
        assert(r.status_code == 200)
        r = requests.get(BASE + "/users/%s/contests/%s" % (self.id, contest_id), auth=self.auth)
        assert(r.status_code == 404)
        r = requests.delete(BASE + "/users/%s/contests/%s" % (self.id, 239482), auth=self.auth)
        assert(r.status_code == 404)
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex
        name = "Joseph Tester"
        nu_data = {"name": name,
                   "username": username,
                   "password": password}
        id = create_user(**nu_data)["id"]
        good = {"username": username, "password": password}
        r = requests.post(BASE + "/login", data=good)
        auth = (r.json["data"]["session_token"], "foo")
        r = requests.post(BASE + "/users/%s/contests" % id, data={"name": "boo"}, auth=auth)
        assert(r.status_code == 200)
        r = requests.post(BASE + "/users/%s/contests" % id, data={"name": "boo"}, auth=self.auth)
        assert(r.status_code == 403)


if __name__ == "__main__":
    unittest.main()