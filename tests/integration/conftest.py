# -*- coding: utf-8 -*-


import pytest
import requests
import logging
import threading
import json

from BaseHTTPServer import HTTPServer
from scoring_api.api import MainHTTPHandler
from scoring_api.store import Store


# Хук для настройки модуля перед стартом тестов.
@pytest.fixture(scope="session", autouse=True)
def setup():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')


class ServerThread(object):
    """
    Класс-обёртка для запуска сервера в параллельном потоке
    """

    def __init__(self, host, http_port, redis_port, redis_db, timeout, n_attempts):
        self.server = HTTPServer((host, http_port), MainHTTPHandler)
        MainHTTPHandler.set_store(host=host, port=redis_port, db=redis_db, timeout=timeout, n_attempts=n_attempts)
        self.store = MainHTTPHandler.store
        logging.info("Starting server at %s" % http_port)
        self.server_thread = threading.Thread(target=self.server.serve_forever)

    def start(self):
        self.server_thread.start()

    def stop(self):
        try:
            self.server.shutdown()
            self.server_thread.join()
            # Это должно удалить все соединения
            del self.store.redis
        except Exception:
            raise

    def shutdown_db_connection(self):
        if self.store:
            return self.store.shutdown_db_connection()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        if exc_val:
            raise


@pytest.fixture
def http_server(server_params):
    server = ServerThread(server_params["HOST"], server_params["HTTP_PORT"], server_params["REDIS_PORT"],
                          server_params["REDIS_DB"], server_params["TIMEOUT"], server_params["N_ATTEMPTS"])
    return server


@pytest.fixture
def store(server_params):
    return Store(host=server_params["HOST"], port=server_params["REDIS_PORT"], db=server_params["REDIS_DB"],
                 timeout=server_params["TIMEOUT"], n_attempts=server_params["N_ATTEMPTS"])


@pytest.fixture
def interests():
    return {0: ['cars', 'cars1'],
            1: ['cars2', 'cars3'],
            2: ['cars4', 'cars5'],
            3: ['cars6', 'cars7'],
            4: ['cars8', 'cars9']}


@pytest.fixture
def scores():
    return {"uid:0849d3d88b7c927197439606640fe47e": {"arguments":
                                                     {"phone": u"78529870534",
                                                      "first_name": "",
                                                      "last_name": u"Иванов",
                                                      "email": u"ivano@mail.ru",
                                                      "gender": 1,
                                                      "birthday": u"12.12.1991"},
                                                     "score": 7.0,
                                                     "calculated_score": 4.5
                                                     },
            "uid:0b286dc61281ff7b05427b92e3626cd0": {"arguments":
                                                     {"phone": u"73434470534",
                                                      "first_name": u"Иван",
                                                      "last_name": u"Иванов",
                                                      "email": u"ivano@mail.ru",
                                                      "gender": 1,
                                                      "birthday": u"12.12.1991"},
                                                     "score": 15.0,
                                                     "calculated_score": 5.0
                                                     }
            }


@pytest.fixture
def interests_request_template():
    payload = {"account": "ivan", "login": "ivan91", "method": "clients_interests",
               "token": "36592bae85a52296530b416e9236c503543d9c0fd835614474ec0344b1c33c5b2de933b041bab4c8f04e9c2994a9dc"
                        "22806b60b08fc3965486fa400f1dc6fbfe"}
    return payload


@pytest.fixture
def online_score_request_template():
    payload = {"account": "ivan", "login": "ivan91", "method": "online_score",
               "token": "36592bae85a52296530b416e9236c503543d9c0fd835614474ec0344b1c33c5b2de933b041bab4c8f04e9c2994a9dc"
                        "22806b60b08fc3965486fa400f1dc6fbfe"}
    return payload


@pytest.fixture
def send_post_request(server_params):
    def send_post_request_with_params(payload):
        url = 'http://{}:{}/method/'.format(server_params["HOST"], server_params["HTTP_PORT"])
        headers = {'content-type': 'application/json'}
        result = requests.post(url, data=json.dumps(payload), headers=headers)
        return result

    return send_post_request_with_params
