# -*- coding: utf-8 -*-

import redis
import time
from redis.exceptions import AuthenticationError, ConnectionError, TimeoutError


class Store(object):

    def __init__(self, host, port, db, timeout, n_attempts):
        self.host = host
        self.port = port
        self.db = db
        self.redis = None
        self.timeout = timeout
        self.n_attempts = n_attempts
        self.cache = dict()
        self.redis_client_addr = None
        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.redis = redis.StrictRedis(host=self.host, port=self.port, db=self.db,
                                           socket_connect_timeout=self.timeout, socket_timeout=self.timeout)
            self.redis_client_addr = self.redis.client_list()[0]["addr"]
        except TimeoutError:
            return False
        except AuthenticationError, error:
            raise error

    def shutdown_db_connection(self):
        self.redis.client_kill(self.redis_client_addr)

    def get(self, key):
        for i in range(self.n_attempts):
            try:
                value = self.redis.get(key)
                return value
            except ConnectionError:
                self.connect_to_db()

    def set(self, key, value):
        for i in range(self.n_attempts):
            try:
                self.redis.set(key, value)
                return True
            except ConnectionError:
                self.connect_to_db()
            except TimeoutError:
                pass

    def cache_get(self, key):
        v = self.cache.get(key, None)
        if v and v["dead_time"] > time.time():
            return v["value"]

        return None

    def cache_set(self, key, value, time_to_live):
        dead_time = time.time() + time_to_live
        self.cache.update({key: {"value": value, "dead_time": dead_time}})

    def flushdb(self):
        return self.redis.flushdb()
