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
from itertools import combinations


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
        minimum_args = (set(('phone', 'email')), set(('first_name', 'last_name')), set(('gender', 'birthday')))
        for filled_pairs in combinations(self.get_filled_fields(), 2):
            if set(filled_pairs) in minimum_args:
                return True


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
    request_errors = mr.is_valid()

    if request_errors:
        raise ValidationError(request_errors)

    if not check_auth(mr):
        raise Forbidden(u"Wrong credentials.")

    return mr


def clients_interests_handler(request, ctx, store):
    """
    Обработчик для запросов по интересам клиента clients_interests
    :param dict request:
    :param dict ctx:
    :param store:
    :return dict:
    """
    mr = get_parsed_request(request)
    ci = ClientsInterestsRequest(mr.arguments)
    ci_errors = ci.is_valid()

    if ci_errors:
        raise ValidationError(ci_errors)

    interests = {client_id: get_interests(None, client_id) for client_id in ci.client_ids}
    ctx.update({'nclients': len(ci.client_ids)})
    return interests


def online_score_handler(request, ctx, store):
    """
    Обработчик для запросов по скорингу online_score
    :param dict request:
    :param dict ctx:
    :param store:
    :return dict:
    """
    mr = get_parsed_request(request)
    score_req = OnlineScoreRequest(mr.arguments)
    score_req_errors = score_req.is_valid()

    if score_req_errors:
        raise ValidationError(score_req_errors)

    if not score_req.validate_arguments():
        raise InvalidRequest(u"Not enough arguments in request: {}".format(mr.arguments))

    if mr.is_admin:
        score = 42
    else:
        score = get_score(None, score_req.phone, score_req.email, score_req.birthday, score_req.gender,
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
            response = METHODS[mr.method](request, ctx, store)
            code = OK
            logging.info(u'Request: {} successfully processed. Result is: {}'.format(request, response))
        else:
            raise InvalidRequest(u"Unknown method '{}'".format(mr.method))

    except InvalidRequest, error:
        logging.error(u'{}'.format(error))
        response, code = error.message, INVALID_REQUEST
    except Forbidden, error:
        response, code = error.message, FORBIDDEN
    except ValidationError, error:
        response, code = error.message, INVALID_REQUEST

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler,
    }
    store = None

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
                except Exception, e:
                    logging.exception(u"Unexpected error: %s" % e.message)
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
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
