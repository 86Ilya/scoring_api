# -*- coding: utf-8 -*-

import hashlib
import datetime

from scoring_api import api
import json
import pytest


class FakeStore(object):
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key, None)

    def set(self, key, value):
        self.store[key] = value

    def cache_get(self, key):
        return self.get(key)

    def cache_set(self, key, value, ttl):
        self.set(key, value)


class TestSuite(object):

    def setup_class(self):
        self.context = {}
        self.headers = {}
        self.settings = FakeStore()
        # Заполним наше фейковое хранилище данными
        fake_interests = [[u'cars', u'cats'], [u'tv', u'cinema'], [u'sport', u'fitness'], [u'swimming', u'walking']]

        for key in range(len(fake_interests)):
            self.settings.set(u"i:{}".format(key), json.dumps(fake_interests[key]))

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.settings)

    def set_valid_auth(self, request):
        if request.get("login") == api.ADMIN_LOGIN:
            request["token"] = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).hexdigest()
        else:
            msg = request.get("account", "") + request.get("login", "") + api.SALT
            request["token"] = hashlib.sha512(msg).hexdigest()

    def test_empty_request(self):
        _, code = self.get_response({})
        assert api.INVALID_REQUEST == code

    @pytest.mark.parametrize(
        "request", [
            {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
            {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
            {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
        ])
    def test_bad_auth(self, request):
        _, code = self.get_response(request)
        assert api.FORBIDDEN == code

    @pytest.mark.parametrize(
        "request", [
            {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
            {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
            {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
        ])
    def test_invalid_method_request(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        assert api.INVALID_REQUEST == code
        assert len(response) > 0

    @pytest.mark.parametrize(
        "request", [
            {},
            {"phone": "79175002040"},
            {"phone": "89175002040", "email": "stupnikov@otus.ru"},
            {"phone": "79175002040", "email": "stupnikovotus.ru"},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
             "first_name": 1},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
             "first_name": "s", "last_name": 2},
            {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
            {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
        ])
    def test_invalid_score_request(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        assert api.INVALID_REQUEST == code, request
        assert len(response) > 0

    @pytest.mark.parametrize(
        "arguments", [
            {"phone": "79175002040", "email": "stupnikov@otus.ru"},
            {"phone": 79175002040, "email": "stupnikov@otus.ru"},
            {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
            {"gender": 0, "birthday": "01.01.2000"},
            {"gender": 2, "birthday": "01.01.2000"},
            {"first_name": "a", "last_name": "b"},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
             "first_name": "a", "last_name": "b"},
        ])
    def test_ok_score_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        assert api.OK == code, request
        score = response.get("score")
        assert isinstance(score, (int, float)) and score >= 0
        assert sorted(self.context["has"]) == sorted(request["arguments"].keys())

    def test_ok_score_admin_request(self):
        arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
        request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        assert api.OK == code
        score = response.get("score")
        assert score == 42

    @pytest.mark.parametrize(
        "request", [
            {},
            {"date": "20.07.2017"},
            {"client_ids": [], "date": "20.07.2017"},
            {"client_ids": {1: 2}, "date": "20.07.2017"},
            {"client_ids": ["1", "2"], "date": "20.07.2017"},
            {"client_ids": [1, 2], "date": "XXX"},
        ])
    def test_invalid_interests_request(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        assert api.INVALID_REQUEST == code, request
        assert len(response) > 0

    @pytest.mark.parametrize(
        "arguments", [
            {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
            {"client_ids": [1, 2], "date": "19.07.2017"},
            {"client_ids": [0]},
        ])
    def test_ok_interests_request(self, arguments):

        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        assert api.OK == code, request
        assert len(request["arguments"]["client_ids"]) == len(response)
        print response.values()
        assert all(v and isinstance(v, list) and all(isinstance(i, basestring) for i in v)
                   for v in response.values()) is True
        assert self.context.get("nclients") == len(request["arguments"]["client_ids"])
