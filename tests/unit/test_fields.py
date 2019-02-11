import pytest

from scoring_api.models import Model, CharField, ArgumentsField, EmailField, PhoneField, DateField, BirthDayField, \
    GenderField, ClientIDsField, ValidationError, InvalidRequest, Forbidden


class ModelWithAllFields(Model):
    char_field = CharField(required=False, nullable=False)
    arguments_field = ArgumentsField(required=False, nullable=False)
    email_field = EmailField(required=False, nullable=False)
    phone_field = PhoneField(required=False, nullable=False)
    date_field = DateField(required=False, nullable=False)
    birthday_field = BirthDayField(required=False, nullable=False)
    gender_field = GenderField(required=False, nullable=False)
    client_ids_field = ClientIDsField(required=False)


class ModelWithRequiredFields(Model):
    char_field_required = CharField(required=True, nullable=False)
    char_field_not_required = CharField(required=False, nullable=False)


class ModelWithNullableFields(Model):
    char_field_nullable = CharField(required=False, nullable=True)
    char_field_not_nullable = CharField(required=False, nullable=False)


def test_fields_with_wrong_types(field_with_wrong_type):
    field_name, original_type, value = field_with_wrong_type
    value_type = type(value).__name__

    check_pattern = u'Field {} must have {} type but value .* has type {}'.format(
        field_name, original_type, value_type).replace('(', '\(').replace(')', '\)')

    with pytest.raises(ValidationError, match=check_pattern):
        fields_container = ModelWithAllFields()
        setattr(fields_container, field_name, value)


def test_required_fields():
    fields_container = ModelWithRequiredFields({})
    errors = getattr(fields_container, "errors", None)
    assert errors is not None
    assert errors["char_field_required"] == "Field char_field_required are required, but value is None"
    assert errors.get("char_field_not_required", None) is None


def test_nullable_fields():
    fields_container = ModelWithNullableFields({"char_field_nullable": None, "char_field_not_nullable": None})
    errors = getattr(fields_container, "errors", None)
    assert errors is not None
    assert errors["char_field_not_nullable"] == "Field char_field_not_nullable are not nullable, but value is None"
    assert errors.get("char_field_nullable", None) is None


# Check fields with correct values


def test_char_field_with_correct_values(char_field_correct_value):
    fields_container = ModelWithAllFields()
    try:
        fields_container.char_field = char_field_correct_value
    except ValidationError, error:
        pytest.fail(error.args)
        return False

    return True


def test_arguments_field_with_correct_values(arguments_field_correct_value):
    fields_container = ModelWithAllFields()
    try:
        fields_container.arguments_field = arguments_field_correct_value
    except ValidationError, error:
        pytest.fail(error.args)
        return False
    return True


def test_email_field_with_correct_values(email_field_correct_value):
    fields_container = ModelWithAllFields()
    try:
        fields_container.email_field = email_field_correct_value
    except ValidationError, error:
        pytest.fail(error.args)
        return False

    return True


def test_phone_field_with_correct_values(phone_field_correct_value):
    fields_container = ModelWithAllFields()
    try:
        fields_container.phone_field = phone_field_correct_value
    except ValidationError, error:
        pytest.fail(error.args)
        return False
    return True


def test_date_field_with_correct_values(date_field_correct_value):
    fields_container = ModelWithAllFields()
    try:
        fields_container.date_field = date_field_correct_value
    except ValidationError, error:
        pytest.fail(error.args)
        return False
    return True


def test_birthday_field_with_correct_values(birthday_field_correct_value):
    fields_container = ModelWithAllFields()
    try:
        fields_container.birthday_field = birthday_field_correct_value
    except ValidationError, error:
        pytest.fail(error.args)
        return False
    return True


def test_gender_field_with_correct_values(gender_field_correct_value):
    fields_container = ModelWithAllFields()
    try:
        fields_container.gender_field = gender_field_correct_value
    except ValidationError, error:
        pytest.fail(error.args)
        return False
    return True


def test_client_ids_field_with_correct_values(client_ids_field_correct_value):
    fields_container = ModelWithAllFields()
    try:
        fields_container.client_ids_field = client_ids_field_correct_value
    except ValidationError, error:
        pytest.fail(error.args)
        return False
    return True


# Next step: check fields with INcorrect values


def test_char_field_with_incorrect_values(char_field_incorrect_value):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.char_field = char_field_incorrect_value


def test_arguments_field_with_incorrect_values(arguments_field_incorrect_value):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.arguments_field = arguments_field_incorrect_value


def test_email_field_with_incorrect_values(email_field_incorrect_value):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.email_field = email_field_incorrect_value


def test_phone_field_with_incorrect_values(phone_field_incorrect_value):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.phone_field = phone_field_incorrect_value


def test_date_field_with_incorrect_values(date_field_incorrect_value):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.date_field = date_field_incorrect_value


def test_birthday_field_with_incorrect_values(birthday_field_incorrect_value):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.birthday_field = birthday_field_incorrect_value


def test_gender_field_with_incorrect_values(gender_field_incorrect_value):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.gender_field = gender_field_incorrect_value


def test_client_ids_field_with_incorrect_values(client_ids_field_incorrect_value):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.client_ids_field = client_ids_field_incorrect_value
