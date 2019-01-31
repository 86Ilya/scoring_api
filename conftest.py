import pytest


# TODO
def id_func(r):
    return "z"


@pytest.fixture(scope="function", params=["abc~!@#$%^&*()_+=-", "a"*256, ""], ids=id_func)
def char_field_correct_value(request):
    return request.param


@pytest.fixture(scope="function", params=["a"*257, 123456798, {}], ids=id_func)
def char_field_incorrect_value(request):
    return request.param


@pytest.fixture(scope="function", params=[{"arg1": 1, "arg2": 2}, {}, {"arg1": "data"}], ids=id_func)
def arguments_field_correct_value(request):
    return request.param


@pytest.fixture(scope="function", params=[[], "", 123], ids=id_func)
def arguments_field_incorrect_value(request):
    return request.param


@pytest.fixture(scope="function", params=["ilya@m.ru", "z@m.r", "ilya.a@gmail.com"], ids=id_func)
def email_field_correct_value(request):
    return request.param


@pytest.fixture(scope="function", params=["www.ya.ru", "", 123], ids=id_func)
def email_field_incorrect_value(request):
    return request.param


@pytest.fixture(scope="function", params=["76542589156", 79876320478, 79999999999], ids=id_func)
def phone_field_correct_value(request):
    return request.param


@pytest.fixture(scope="function", params=["88002004040", 799966600441, []], ids=id_func)
def phone_field_incorrect_value(request):
    return request.param


@pytest.fixture(scope="function", params=["10.04.1986", "29.02.2016", "01.01.1900"], ids=id_func)
def date_field_correct_value(request):
    return request.param


@pytest.fixture(scope="function", params=["XXX", 10041986, "29.02.2019"], ids=id_func)
def date_field_incorrect_value(request):
    return request.param


@pytest.fixture(scope="function", params=["10.04.1986"], ids=id_func)
def birthday_field_correct_value(request):
    return request.param


@pytest.fixture(scope="function", params=["12.12.1880"], ids=id_func)
def birthday_field_incorrect_value(request):
    return request.param


@pytest.fixture(scope="function", params=[0, 1, 2], ids=id_func)
def gender_field_correct_value(request):
    return request.param


@pytest.fixture(scope="function", params=["M", "F", 4], ids=id_func)
def gender_field_incorrect_value(request):
    return request.param


@pytest.fixture(scope="function", params=[[1, 2, 3], [1, 2], [1]], ids=id_func)
def client_ids_field_correct_value(request):
    return request.param


@pytest.fixture(scope="function", params=[{1: 2, 3: 4}, "1,2,3", 123], ids=id_func)
def client_ids_field_incorrect_value(request):
    return request.param
