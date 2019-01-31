# -*- coding: utf-8 -*-

import redis
import time


class Store(object):

    def __init__(self, host, port, db, timeout, n_attempts):
        self.host = host
        self.port = port
        self.db = db
        self.redis = None
        self.timeout = timeout
        self.n_attempts = n_attempts
        self.cache = dict()

    # TODO -> init?
    def start(self):
        self.redis = redis.StrictRedis(host=self.host, port=self.port, db=self.db)

    def stop(self):
        pass

    def get(self, key):
        return self.redis.get(key)

    def cache_get(self, key):
        v = self.cache.get(key, None)
        if v and v["dead_time"] < time.time():
            return v["value"]

        return None

    def cache_set(self, key, value, time_to_live):
        dead_time = time.time() + time_to_live
        self.cache.set(key, {"value": value, "dead_time": dead_time})