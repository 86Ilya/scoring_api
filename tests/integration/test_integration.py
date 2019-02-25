# -*- coding: utf-8 -*-

# import traceback
import json
import time
import pytest
import redis
from redis.exceptions import ConnectionError, TimeoutError


def test_get_interests_with_values_in_db_when_db_works_fine(http_server, store, interests, interests_request_template,
                                                            send_post_request):
    # Очистим тестовую базу
    store.flushdb()
    # Заполним наше хранилище тестовыми данными
    for key, value in interests.iteritems():
        # print "i:{}".format(key), value
        store.set(u"i:{}".format(key), json.dumps(value))

    payload = interests_request_template.copy()

    with http_server:
        try:
            for key, value in interests.iteritems():
                payload.update({"arguments": {"client_ids": [key]}})
                response = send_post_request(payload)
                interests_dict = json.loads(response.content).get("response", None)
                assert interests_dict[unicode(key)] == value

        except Exception, error:
            pytest.fail(error.message)

    return True


def test_get_interests_with_values_in_db_when_db_occasionally_stops(http_server, store, interests, send_post_request,
                                                                    interests_request_template):
    # Очистим тестовую базу
    store.flushdb()
    # Заполним наше хранилище тестовыми данными
    for key, value in interests.iteritems():
        # print "i:{}".format(key), value
        store.set(u"i:{}".format(key), json.dumps(value))

    payload = interests_request_template.copy()

    with http_server:
        try:
            for key, value in interests.iteritems():
                payload.update({"arguments": {"client_ids": [key]}})
                # Остановим подключение к базе данных
                http_server.shutdown_db_connection()
                response = send_post_request(payload)
                interests_dict = json.loads(response.content).get("response", None)
                assert interests_dict[unicode(key)] == value

        except Exception, error:
            pytest.fail(error.args[0])

    return True


def test_get_interests_with_values_in_db_when_db_works_slowly(http_server, store, interests, monkeypatch,
                                                              interests_request_template, caplog, send_post_request):
    with monkeypatch.context() as m:
        # сохраним старый метод, он нам пригодится, чтобы отдавать реальные значения
        old_get = redis.StrictRedis.get

        # Фейковый метод для редиса, будет вначале выкидывать ошибку TimeoutError, а уже на третий раз отдавать
        # реальное значение
        def fake_get(self, key):
            if fake_get.raise_counter < 3:
                fake_get.raise_counter += 1
                # Добавим символичное ожидание, как будто наша бд реально медленно работает.
                time.sleep(1)
                raise TimeoutError("Fake timeout error")
            else:
                real_value = old_get(self, key)
                fake_get.raise_counter = 0
                return real_value

        fake_get.raise_counter = 0
        m.setattr(redis.StrictRedis, "get", fake_get)

        # Очистим тестовую базу
        store.flushdb()
        # Заполним наше хранилище тестовыми данными
        for key, value in interests.iteritems():
            store.set(u"i:{}".format(key), json.dumps(value))

        payload = interests_request_template.copy()

        with http_server:
            try:
                for key, value in interests.iteritems():
                    payload.update({"arguments": {"client_ids": [key]}})
                    response = send_post_request(payload)
                    interests_dict = json.loads(response.content).get("response", None)
                    last_log = caplog.records.pop()
                    assert u"We have timeout error in 'get' operation: Fake timeout error." \
                           u" Trying to reconnect. Attempt" in last_log.message
                    assert interests_dict[unicode(key)] == value

            except Exception, error:
                pytest.fail(error.args[0])

    return True


def test_raise_error_in_get_interests_when_db_didnt_answer(http_server, interests, monkeypatch, send_post_request,
                                                           interests_request_template, caplog):
    with monkeypatch.context() as m:

        # Фейковый метод для редиса, будет всегда выкидывать ошибку TimeoutError
        def fake_get(self, key):
            # Добавим символичное ожидание, как будто наша бд реально медленно работает.
            time.sleep(1)
            raise ConnectionError("Fake timeout error")

        m.setattr(redis.StrictRedis, "get", fake_get)

        payload = interests_request_template.copy()

        with http_server:
            try:
                for key, value in interests.iteritems():
                    payload.update({"arguments": {"client_ids": [key]}})
                    response = send_post_request(payload)
                    json.loads(response.content).get("response", None)
                    last_log = caplog.records.pop()
                    assert u"Error while getting value from db:" \
                           u" We did 5 unsuccessful attempts to Get value from DB" in last_log.message
                    last_log = caplog.records.pop()
                    assert u"We have connection error in 'get' operation:" \
                           u" Fake timeout error. Trying to reconnect." in last_log.message

            except Exception, error:
                pytest.fail(error.args[0])

    return True


def test_raise_error_in_get_interests_when_db_cant_connect(http_server, interests, caplog, interests_request_template,
                                                           send_post_request):
    payload = interests_request_template.copy()

    with http_server:
        try:
            # Остановим подключение к базе данных
            http_server.shutdown_db_connection()
            # Грубо подменим изначальный порт БД
            http_server.store.port = 12345
            for key, value in interests.iteritems():
                payload.update({"arguments": {"client_ids": [key]}})
                response = send_post_request(payload)
                json.loads(response.content).get("response", None)
                last_log = caplog.records.pop()
                assert u"Error while getting value from db:" \
                       u" We did 5 unsuccessful attempts to Get value from DB" in last_log.message
                last_log = caplog.records.pop()
                # print last_log.message
                assert u"We have connection error in 'get' operation: Error 111" in last_log.message

        except Exception, error:
            pytest.fail(error.args[0])

    return True


def test_get_score_with_values_in_cache_when_cache_works_fine(http_server, scores, online_score_request_template,
                                                              send_post_request, store):
    # Очистим тестовый кэш
    store.flushcache()

    # Заполним наше хранилище тестовыми данными
    for key, value in scores.iteritems():
        store.cache_set(u"{}".format(key), json.dumps(value["score"]), 60 * 60)

    payload = online_score_request_template.copy()

    with http_server:
        try:
            for key, value in scores.iteritems():
                payload.update({"arguments": value["arguments"]})
                response = send_post_request(payload)
                scores_dict = json.loads(response.content).get("response", None)
                assert scores_dict[u"score"] == value["score"]

        except Exception, error:
            pytest.fail(error.message)

    return True


def test_get_score_calculate_score_when_cache_not_exist(http_server, scores, online_score_request_template, store,
                                                        send_post_request):
    # Очистим тестовый кэш
    store.flushcache()
    payload = online_score_request_template.copy()

    with http_server:
        try:
            for key, value in scores.iteritems():
                payload.update({"arguments": value["arguments"]})
                response = send_post_request(payload)
                scores_dict = json.loads(response.content).get("response", None)
                assert scores_dict[u"score"] == value["calculated_score"]

        except Exception, error:
            pytest.fail(error)

    return True


def test_get_score_recalculate_score_when_value_expired(http_server, scores, online_score_request_template,
                                                        send_post_request, store):
    # Очистим тестовый кэш
    store.flushcache()
    # Заполним наше хранилище тестовыми данными
    for key, value in scores.iteritems():
        store.cache_set(u"{}".format(key), json.dumps(value["score"]), 1)

    time.sleep(2)
    payload = online_score_request_template.copy()

    with http_server:
        try:
            for key, value in scores.iteritems():
                payload.update({"arguments": value["arguments"]})
                response = send_post_request(payload)
                scores_dict = json.loads(response.content).get("response", None)
                assert scores_dict[u"score"] == value["calculated_score"]

        except Exception, error:
            pytest.fail(error.message)

    return True
