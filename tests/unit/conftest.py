# -*- coding: utf-8 -*-
import pytest
import datetime


@pytest.fixture(
    params=[
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
        {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
    ])
def bad_auth_values(request):
    return request.param


@pytest.fixture(
    params=[
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
        {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
    ])
def invalid_method_request_values(request):
    return request.param


@pytest.fixture(
    params=[
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": 1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "s", "last_name": 2},
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
    ])
def invalid_score_request_values(request):
    return {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": request.param}


@pytest.fixture(
    params=[
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "a", "last_name": "b"},
    ])
def ok_score_request_values(request):
    return {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": request.param}


@pytest.fixture(
    params=[
        {},
        {"date": "20.07.2017"},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
    ])
def invalid_interests_request_values(request):
    return {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": request.param}


@pytest.fixture(
    params=[
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ])
def ok_interests_request_values(request):
    return {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": request.param}


# Check type mismatch
@pytest.fixture(params=[
    ('char_field', basestring, {1: "123"}),
    ('arguments_field', dict, [1, 2, 3, 4, 5]),
    ('email_field', basestring, {1: "123"}),
    ('phone_field', (basestring, int), [81234561232]),
    ('gender_field', int, "1"),
    ('client_ids_field', list, {1: "123"})])
def field_with_wrong_type(request):
    return request.param


@pytest.fixture(params=["abc~!@#$%^&*()_+=-", "a" * 256, u"aaaa"])
def char_field_correct_value(request):
    return request.param


@pytest.fixture(params=["a" * 257, 123456798, {}])
def char_field_incorrect_value(request):
    return request.param


@pytest.fixture(params=[{"arg1": 1, "arg2": 2}, {"arg2": [1, 2]}, {"arg1": "data"}])
def arguments_field_correct_value(request):
    return request.param


@pytest.fixture(params=[[], "", 123])
def arguments_field_incorrect_value(request):
    return request.param


@pytest.fixture(params=["ilya@m.ru", "z@m.r", "ilya.a@gmail.com"])
def email_field_correct_value(request):
    return request.param


@pytest.fixture(params=["www.ya.ru", "", 123])
def email_field_incorrect_value(request):
    return request.param


@pytest.fixture(params=["76542589156", 79876320478, 79999999999])
def phone_field_correct_value(request):
    return request.param


@pytest.fixture(params=["88002004040", 799966600441, []])
def phone_field_incorrect_value(request):
    return request.param


@pytest.fixture(params=[u"10.04.1986", "29.02.2016", "01.01.1900"])
def date_field_correct_value(request):
    return request.param


@pytest.fixture(params=["XXX", 10041986, "29.02.2019"])
def date_field_incorrect_value(request):
    return request.param


@pytest.fixture(params=["10.04.1986"])
def birthday_field_correct_value(request):
    return request.param


@pytest.fixture(params=["12.12.1880"])
def birthday_field_incorrect_value(request):
    return request.param


@pytest.fixture(params=[0, 1, 2])
def gender_field_correct_value(request):
    return request.param


@pytest.fixture(params=["M", "F", 4])
def gender_field_incorrect_value(request):
    return request.param


@pytest.fixture(params=[[1, 2, 3], [1, 2], [1]])
def client_ids_field_correct_value(request):
    return request.param


@pytest.fixture(params=[{1: 2, 3: 4}, "1,2,3", 123])
def client_ids_field_incorrect_value(request):
    return request.param
