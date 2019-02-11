# -*- coding: utf-8 -*-


import logging
import redis
import time
from redis.exceptions import AuthenticationError, ConnectionError, TimeoutError, ResponseError, RedisError


class GetValueError(RedisError):
    pass


class SetValueError(RedisError):
    pass


class Store(object):

    def __init__(self, host, port, db, timeout, n_attempts, connect_at_init=True):
        self.host = host
        self.port = port
        self.db = db
        self.redis = None
        self.timeout = timeout
        self.n_attempts = n_attempts
        self.cache = dict()
        if connect_at_init:
            self.connect_to_db()
        self.logger = logging.getLogger("Store")
        self.logger.setLevel(logging.INFO)

    def connect_to_db(self):
        try:
            self.redis = redis.StrictRedis(host=self.host, port=self.port, db=self.db,
                                           socket_connect_timeout=self.timeout, socket_timeout=self.timeout)
        except TimeoutError:
            return False
        except AuthenticationError, error:
            raise error

    def shutdown_db_connection(self):
        try:
            redis_client_addr = self.redis.client_list()[0]["addr"]
            return self.redis.client_kill(redis_client_addr)
        except Exception, error:
            self.logger.error(u"Error occurred while trying to shutdown db: {}".format(error.args[0]))
            raise

    def get(self, key):
        for i in range(self.n_attempts):
            try:
                value = self.redis.get(key)
                return value
            except ConnectionError, error:
                self.logger.error(u"We have connection error in 'get' operation: {}."
                                  u" Trying to reconnect. Attempt #{}".format(error.args[0], i))
                # timeout при попытке переподключиться
                time.sleep(self.timeout)
                self.connect_to_db()
            except TimeoutError, error:
                # redis client имеет свой timeout, так что дополнительно ждать тут нет смысла
                self.logger.error(u"We have timeout error in 'get' operation: {}."
                                  u" Trying to reconnect. Attempt #{}".format(error.args[0], i))
        raise GetValueError(u"We did {} unsuccessful attempts to Get value from DB".format(i))

    def set(self, key, value):
        for i in range(self.n_attempts):
            try:
                self.redis.set(key, value)
                return True
            except ConnectionError, error:
                self.logger.error(u"We have connection error in 'set' operation: {}."
                                  u" Trying to reconnect. Attempt #{}".format(error.args[0], i))
                # wait timeout on reconnect
                time.sleep(self.timeout)
                self.connect_to_db()
            except TimeoutError:
                # redis client имеет свой timeout, так что дополнительно ждать тут нет смысла
                self.logger.error(u"We have timeout error in 'set' operation: {}."
                                  u" Trying to reconnect. Attempt #{}".format(error.args[0], i))
        raise SetValueError(u"We did {} unsuccessful attempts to Set value in DB".format(i))

    def cache_get(self, key, default=None):
        try:
            value_and_ttl = self.cache.get(key, None)
            if value_and_ttl and value_and_ttl["dead_time"] > time.time():
                return value_and_ttl["value"]
        except Exception, error:
            self.logger.error(u"We have error while trying to get value from cache: {}".format(error.args[0]))
            raise

        return default

    def cache_set(self, key, value, time_to_live):
        dead_time = time.time() + time_to_live
        self.cache.update({key: {"value": value, "dead_time": dead_time}})

    def flushdb(self):
        return self.redis.flushdb()
