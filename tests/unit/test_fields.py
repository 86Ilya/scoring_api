import pytest

from scoring_api.models import Model, CharField, ArgumentsField, EmailField, PhoneField, DateField, BirthDayField, \
    GenderField, ClientIDsField, ValidationError


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


# Check type mismatch
@pytest.mark.parametrize("test_input", [
    ('char_field', basestring, {1: "123"}),
    ('arguments_field', dict, [1, 2, 3, 4, 5]),
    ('email_field', basestring, {1: "123"}),
    ('phone_field', (basestring, int), [81234561232]),
    ('gender_field', int, "1"),
    ('client_ids_field', list, {1: "123"})])
def test_fields_with_wrong_types(test_input):
    field_name, original_type, value = test_input
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


@pytest.mark.parametrize("test_input", ["abc~!@#$%^&*()_+=-", "a" * 256, u"aaaa"])
def test_char_field_with_correct_values(test_input):
    fields_container = ModelWithAllFields()
    fields_container.char_field = test_input


@pytest.mark.parametrize("test_input", [{"arg1": 1, "arg2": 2}, {"arg2": [1, 2]}, {"arg1": "data"}])
def test_arguments_field_with_correct_values(test_input):
    fields_container = ModelWithAllFields()
    fields_container.arguments_field = test_input


@pytest.mark.parametrize("test_input", ["ilya@m.ru", "z@m.r", "ilya.a@gmail.com"])
def test_email_field_with_correct_values(test_input):
    fields_container = ModelWithAllFields()
    fields_container.email_field = test_input


@pytest.mark.parametrize("test_input", [0, 1, 2])
def test_gender_field_with_correct_values(test_input):
    fields_container = ModelWithAllFields()
    fields_container.gender_field = test_input


@pytest.mark.parametrize("test_input", [[1, 2, 3], [1, 2], [1]])
def test_client_ids_field_with_correct_values(test_input):
    fields_container = ModelWithAllFields()
    fields_container.client_ids_field = test_input


# Next step: check fields with INcorrect values


@pytest.mark.parametrize("test_input", ["a" * 257, 123456798, {}])
def test_char_field_with_incorrect_values(test_input):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.char_field = test_input


@pytest.mark.parametrize("test_input", [[], "", 123])
def test_arguments_field_with_incorrect_values(test_input):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.arguments_field = test_input


@pytest.mark.parametrize("test_input", ["www.ya.ru", "", 123])
def test_email_field_with_incorrect_values(test_input):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.email_field = test_input


@pytest.mark.parametrize("test_input", ["88002004040", 799966600441, []])
def test_phone_field_with_incorrect_values(test_input):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.phone_field = test_input


@pytest.mark.parametrize("test_input", ["XXX", 10041986, "29.02.2019"])
def test_date_field_with_incorrect_values(test_input):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.date_field = test_input


@pytest.mark.parametrize("test_input", ["12.12.1880"])
def test_birthday_field_with_incorrect_values(test_input):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.birthday_field = test_input


@pytest.mark.parametrize("test_input", ["M", "F", 4])
def test_gender_field_with_incorrect_values(test_input):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.gender_field = test_input


@pytest.mark.parametrize("test_input", [{1: 2, 3: 4}, "1,2,3", 123])
def test_client_ids_field_with_incorrect_values(test_input):
    fields_container = ModelWithAllFields()
    with pytest.raises(ValidationError):
        fields_container.client_ids_field = test_input
