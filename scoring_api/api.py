#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import logging
import hashlib
import uuid

from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from scoring import get_score, get_interests
from models import Model, CharField, ArgumentsField, EmailField, PhoneField, DateField, BirthDayField, GenderField, \
    ClientIDsField, ValidationError, InvalidRequest, Forbidden
from store import Store, GetValueError, SetValueError


SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

DEFAULT = {
    'HOST': '127.0.0.1',
    'HTTP_PORT': 8080,
    'REDIS_PORT': 6379,
    'REDIS_DB': 0,
    'TIMEOUT': 1,
    'N_ATTEMPTS': 5
}


class ClientsInterestsRequest(Model):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Model):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate_arguments(self):
        if (self.phone and self.email) or (self.first_name and self.last_name)\
                or (self.gender is not None and self.birthday):
            return True
        else:
            return False


class MethodRequest(Model):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True

    return False


def get_parsed_request(request):
    """
    Функция разбирает полученный запрос на структуру MethodRequest и возвращает его,
    если какое-либо поле не удовлетворяет нашим требованиям, то делает raise ошибки
    :param dict request:
    :return MethodRequest:
    """
    body = request.get('body')
    if not body:
        raise InvalidRequest(u"Request has empty 'body'")

    mr = MethodRequest(body)

    if not mr.is_valid():
        raise ValidationError(mr.errors)

    if not check_auth(mr):
        raise Forbidden(u"Wrong credentials.")

    return mr


def clients_interests_handler(mr, ctx, store):
    """
    Обработчик для запросов по интересам клиента clients_interests
    :param MethodRequest mr:
    :param dict ctx:
    :param store:
    :return dict:
    """
    ci = ClientsInterestsRequest(mr.arguments)

    if not ci.is_valid():
        raise ValidationError(ci.errors)

    interests = {client_id: get_interests(store, client_id) for client_id in ci.client_ids}
    ctx.update({'nclients': len(ci.client_ids)})
    return interests


def online_score_handler(mr, ctx, store):
    """
    Обработчик для запросов по скорингу online_score
    :param MethodRequest mr:
    :param dict ctx:
    :param store:
    :return dict:
    """
    score_req = OnlineScoreRequest(mr.arguments)

    if not score_req.is_valid():
        raise ValidationError(score_req.errors)
    if not score_req.validate_arguments():
        raise InvalidRequest(u"Not enough arguments in request: {}".format(mr.arguments))

    if mr.is_admin:
        score = 42
    else:
        score = get_score(store, score_req.phone, score_req.email, score_req.birthday, score_req.gender,
                          score_req.first_name, score_req.last_name)

    ctx.update({'has': score_req.get_filled_fields()})
    response = {'score': score}

    return response


def method_handler(request, ctx, store):
    """
    Основной обработчик методов. Все запросы, в которых указан путь method приходят сюда
    :param dict request:
    :param dict ctx:
    :param store:
    :return:
    """
    response, code = None, None

    METHODS = {
        "online_score": online_score_handler,
        "clients_interests": clients_interests_handler,
    }

    try:
        logging.info(u'Processing request: {}'.format(request))
        mr = get_parsed_request(request)
        if mr.method in METHODS:
            response = METHODS[mr.method](mr, ctx, store)
            code = OK
            logging.info(u'Request: {} successfully processed. Result is: {}'.format(request, response))
        else:
            raise InvalidRequest(u"Unknown method '{}'".format(mr.method))

    except InvalidRequest, error:
        logging.error(u'{}'.format(error))
        response, code = error.args, INVALID_REQUEST
    except Forbidden, error:
        response, code = error.args, FORBIDDEN
    except ValidationError, error:
        response, code = error.args, INVALID_REQUEST

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler,
    }

    store = None

    @classmethod
    def set_store(cls, host, port, db, timeout, n_attempts):
        cls.store = Store(host=host, port=port, db=db, timeout=timeout, n_attempts=n_attempts)

    @staticmethod
    def get_request_id(headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception, e:
            logging.error(u"Bad request: %s" % e.message)
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except SetValueError, error:
                    logging.error(u"Error while setting value to db: %s" % error.args[0])
                except GetValueError, error:
                    logging.error(u"Error while getting value from db: %s" % error.args[0])
                except Exception, error:
                    logging.exception(u"Unexpected error: %s" % error.args[0])
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=DEFAULT['HTTP_PORT'])
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--redis-port", dest='redis_host', action="store", default=DEFAULT['REDIS_PORT'])
    op.add_option("--redis-host", dest='redis_port', action="store", default=DEFAULT['HOST'])
    op.add_option("--redis-db", dest='redis_db', action="store", default=DEFAULT['REDIS_DB'])
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer((DEFAULT['HOST'], opts.port), MainHTTPHandler)
    MainHTTPHandler.set_store(opts.redis_host, opts.redis_port, opts.redis_db, DEFAULT['TIMEOUT'],
                              DEFAULT['N_ATTEMPTS'])
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
