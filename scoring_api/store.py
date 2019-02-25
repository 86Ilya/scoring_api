# -*- coding: utf-8 -*-


import logging
import redis
import time
from redis.exceptions import AuthenticationError, ConnectionError, TimeoutError, ResponseError, RedisError


class GetValueError(RedisError):
    pass


class SetValueError(RedisError):
    pass


def reconnect(func):
    def wrapper(self, *args):
        name = func.__name__
        for i in range(self.n_attempts):
            try:
                value = func(self, *args)
                return value
            except ConnectionError, error:
                self.logger.error(u"We have connection error in '{}' operation: {}."
                                  u" Trying to reconnect. Attempt #{}".format(name, error.args[0], i))
                # timeout при попытке переподключиться
                time.sleep(self.timeout)
                self.connect_to_db()
            except TimeoutError, error:
                # redis client имеет свой timeout, так что дополнительно ждать тут нет смысла
                self.logger.error(u"We have timeout error in '{}' operation: {}."
                                  u" Trying to reconnect. Attempt #{}".format(name, error.args[0], i))
        raise GetValueError(u"We did {} unsuccessful attempts to Get value from DB".format(self.n_attempts))

    return wrapper


class Store(object):

    def __init__(self, host, port, db, timeout, n_attempts, connect_at_init=True):
        self.host = host
        self.port = port
        self.db = db
        self.redis = None
        self.timeout = timeout
        self.n_attempts = n_attempts
        self.cache = None
        if connect_at_init:
            self.connect_to_db()
        self.logger = logging.getLogger("Store")
        self.logger.setLevel(logging.INFO)

    def connect_to_db(self):
        self.redis = redis.StrictRedis(host=self.host, port=self.port, db=self.db,
                                       socket_connect_timeout=self.timeout, socket_timeout=self.timeout)
        # Для кеша будем использовать аналогичное хранилище
        self.cache = self.redis

    def shutdown_db_connection(self):
        try:
            redis_client_addr = self.redis.client_list()[0]["addr"]
            return self.redis.client_kill(redis_client_addr)
        except Exception, error:
            self.logger.error(u"Error occurred while trying to shutdown db: {}".format(error.args[0]))
            raise

    @reconnect
    def get(self, key):
        value = self.redis.get(key)
        return value

    @reconnect
    def set(self, key, value):
        self.redis.set(key, value)
        return True

    def cache_get(self, key, default=None):
        try:
            value = self.cache.get(u"cache:" + key)
            return value
        except Exception as error:
            self.logger.error(u"We have error while trying to get value from cache: {}".format(error))
            return default

    def cache_set(self, key, value, time_to_live):
        self.cache.set(u"cache:" + key, value, ex=time_to_live)

    def flushdb(self):
        return self.redis.flushdb()

    def flushcache(self):
        return self.cache.flushdb()
