# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="module")
def server_params():
    return {
        'HOST': '127.0.0.1',
        'HTTP_PORT': 8080,
        'REDIS_PORT': 6379,
        'REDIS_DB': 0,
        'TIMEOUT': 1,
        'N_ATTEMPTS': 5
    }
