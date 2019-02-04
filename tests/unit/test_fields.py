import pytest

from scoring_api import api
from scoring_api.models import Model, CharField, ArgumentsField, EmailField, PhoneField, DateField, BirthDayField, \
    GenderField, ClientIDsField


class AllValues(Model):
    char_field = CharField(required=False, nullable=True)
    arguments_field = ArgumentsField(required=True, nullable=True)
    email_field = EmailField(required=False, nullable=True)
    phone_field = PhoneField(required=False, nullable=True)
    date_field = DateField(required=False, nullable=True)
    birthday_field = BirthDayField(required=False, nullable=True)
    gender_field = GenderField(required=False, nullable=True)
    client_ids_field = ClientIDsField(required=True)


def test_char_field_with_correct_values(char_field_correct_value):
    fields_container = AllValues()
    try:
        fields_container.char_field = char_field_correct_value
    except ValueError, error:
        pytest.fail(error.args)
        return False

    return True


# Check fields with correct values

def test_arguments_field_with_correct_values(arguments_field_correct_value):
    fields_container = AllValues()
    try:
        fields_container.arguments_field = arguments_field_correct_value
    except ValueError, error:
        pytest.fail(error.args)
        return False
    return True


def test_email_field_with_correct_values(email_field_correct_value):
    fields_container = AllValues()
    try:
        fields_container.email_field = email_field_correct_value
    except ValueError, error:
        pytest.fail(error.args)
        return False

    return True


def test_phone_field_with_correct_values(phone_field_correct_value):
    fields_container = AllValues()
    try:
        fields_container.phone_field = phone_field_correct_value
    except ValueError, error:
        pytest.fail(error.args)
        return False
    return True


def test_date_field_with_correct_values(date_field_correct_value):
    fields_container = AllValues()
    try:
        fields_container.date_field = date_field_correct_value
    except ValueError, error:
        pytest.fail(error.args)
        return False
    return True


def test_birthday_field_with_correct_values(birthday_field_correct_value):
    fields_container = AllValues()
    try:
        fields_container.birthday_field = birthday_field_correct_value
    except ValueError, error:
        pytest.fail(error.args)
        return False
    return True


def test_gender_field_with_correct_values(gender_field_correct_value):
    fields_container = AllValues()
    try:
        fields_container.gender_field = gender_field_correct_value
    except ValueError, error:
        pytest.fail(error.args)
        return False
    return True


def test_client_ids_field_with_correct_values(client_ids_field_correct_value):
    fields_container = AllValues()
    try:
        fields_container.client_ids_field = client_ids_field_correct_value
    except ValueError, error:
        pytest.fail(error.args)
        return False
    return True


# Next step: check fields with INcorrect values


def test_char_field_with_incorrect_values(char_field_incorrect_value):
    fields_container = AllValues()
    try:
        fields_container.char_field = char_field_incorrect_value
    except ValueError:
        return True
    pytest.fail("This value {} should raise error, but not".format(char_field_incorrect_value))


def test_arguments_field_with_incorrect_values(arguments_field_incorrect_value):
    fields_container = AllValues()
    try:
        fields_container.arguments_field = arguments_field_incorrect_value
    except ValueError:
        return True
    pytest.fail("This value {} should raise error, but not".format(arguments_field_incorrect_value))


def test_email_field_with_incorrect_values(email_field_incorrect_value):
    fields_container = AllValues()
    try:
        fields_container.email_field = email_field_incorrect_value
    except ValueError:
        return True
    pytest.fail("This value {} should raise error, but not".format(email_field_incorrect_value))


def test_phone_field_with_incorrect_values(phone_field_incorrect_value):
    fields_container = AllValues()
    try:
        fields_container.phone_field = phone_field_incorrect_value
    except ValueError:
        return True
    pytest.fail("This value {} should raise error, but not".format(phone_field_incorrect_value))


def test_date_field_with_incorrect_values(date_field_incorrect_value):
    fields_container = AllValues()
    try:
        fields_container.date_field = date_field_incorrect_value
    except ValueError:
        return True
    pytest.fail("This value {} should raise error, but not".format(date_field_incorrect_value))


def test_birthday_field_with_incorrect_values(birthday_field_incorrect_value):
    fields_container = AllValues()
    try:
        fields_container.birthday_field = birthday_field_incorrect_value
    except ValueError:
        return True
    pytest.fail("This value {} should raise error, but not".format(birthday_field_incorrect_value))


def test_gender_field_with_incorrect_values(gender_field_incorrect_value):
    fields_container = AllValues()
    try:
        fields_container.gender_field = gender_field_incorrect_value
    except ValueError:
        return True
    pytest.fail("This value {} should raise error, but not".format(gender_field_incorrect_value))


def test_client_ids_field_with_incorrect_values(client_ids_field_incorrect_value):
    fields_container = AllValues()
    try:
        fields_container.client_ids_field = client_ids_field_incorrect_value
    except ValueError:
        return True
    pytest.fail("This value {} should raise error, but not".format(client_ids_field_incorrect_value))
