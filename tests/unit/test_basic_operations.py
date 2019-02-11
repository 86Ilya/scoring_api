import hashlib
import datetime

from scoring_api import api
from scoring_api.store import Store
import json
import pytest


class TestSuite(object):
    settings = None

    @pytest.fixture(autouse=True, scope='class')
    def _prepare(self, server_params):
        cls = self.__class__
        cls.settings = Store(server_params['HOST'], server_params['REDIS_PORT'], server_params['REDIS_DB'],
                             server_params['TIMEOUT'], server_params['N_ATTEMPTS'])
        cls.settings.flushdb()
        for key in range(0, 4):
            cls.settings.set(u"i:{}".format(key), json.dumps(['cars', 'cats']))

    def setup_class(self):
        self.context = {}
        self.headers = {}

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

    def test_bad_auth(self, bad_auth_values):
        _, code = self.get_response(bad_auth_values)
        assert api.FORBIDDEN == code

    def test_invalid_method_request(self, invalid_method_request_values):
        self.set_valid_auth(invalid_method_request_values)
        response, code = self.get_response(invalid_method_request_values)
        assert api.INVALID_REQUEST == code
        assert len(response) > 0

    def test_invalid_score_request(self, invalid_score_request_values):
        self.set_valid_auth(invalid_score_request_values)
        response, code = self.get_response(invalid_score_request_values)
        assert api.INVALID_REQUEST == code, invalid_score_request_values
        assert len(response) > 0

    def test_ok_score_request(self, ok_score_request_values):
        self.set_valid_auth(ok_score_request_values)
        response, code = self.get_response(ok_score_request_values)
        assert api.OK == code, ok_score_request_values
        score = response.get("score")
        assert isinstance(score, (int, float)) and score >= 0
        assert sorted(self.context["has"]) == sorted(ok_score_request_values["arguments"].keys())

    def test_ok_score_admin_request(self):
        arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
        request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        assert api.OK == code
        score = response.get("score")
        assert score == 42

    def test_invalid_interests_request(self, invalid_interests_request_values):
        self.set_valid_auth(invalid_interests_request_values)
        response, code = self.get_response(invalid_interests_request_values)
        assert api.INVALID_REQUEST == code, invalid_interests_request_values
        assert len(response) > 0

    def test_ok_interests_request(self, ok_interests_request_values):
        self.set_valid_auth(ok_interests_request_values)
        response, code = self.get_response(ok_interests_request_values)
        assert api.OK == code, ok_interests_request_values
        assert len(ok_interests_request_values["arguments"]["client_ids"]) == len(response)
        assert all(v and isinstance(v, list) and all(isinstance(i, basestring) for i in v)
                   for v in response.values()) is True
        assert self.context.get("nclients") == len(ok_interests_request_values["arguments"]["client_ids"])
