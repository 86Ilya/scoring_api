# -*- coding: utf-8 -*-

import re
import datetime
import abc


class ValidationError(ValueError):
    pass


class InvalidRequest(ValueError):
    pass


class Forbidden(ValueError):
    pass


class Field(object):
    """Базовый класс определяющий поле. От него наследуются все другие поля."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable
        self.pattern = None
        self.basetype = basestring
        self.name = None

    def __set__(self, instance, value):
        if instance:
            if value is None and self.required is True:
                raise ValidationError(
                    u'Field {} are required, but value is None'.format(self.name))
            elif value is None and not self.nullable:
                raise ValidationError(
                    u'Field {} are not nullable, but value is None'.format(self.name))
            elif not isinstance(value, self.basetype):
                raise ValidationError(
                    u'Field {} must have {} type but value {} has type {}'.format(self.name, self.basetype, value,
                                                                                  type(value).__name__))
            elif self.check_nullable(value) or self.check_value(value):
                instance.__dict__[self.name] = value
            else:
                raise ValidationError(
                    u'Field {} are not compatible with value "{}"'.format(self.name, value))

    def __get__(self, instance, owner):
        if instance:
            return instance.__dict__.get(self.name, None)
        else:
            return self

    @abc.abstractmethod
    def check_value(self, value):
        if value is not None and isinstance(value, self.basetype):
            # все строки у нас в utf-8. re корректно обрабатывает их
            # проверка нужна для типов int, float итп
            if not isinstance(value, basestring):
                value = str(value)
            return re.match(self.pattern, value)

    def check_nullable(self, value):
        if self.nullable and not isinstance(value, int) and (
                value is None or (isinstance(value, self.basetype) and len(value) == 0)):
            return True
        else:
            return False


class CharField(Field):
    def __init__(self, required=False, nullable=False):
        super(CharField, self).__init__(required, nullable)
        self.pattern = r'(.){0,256}'

    def check_value(self, value):
        return super(CharField, self).check_value(value)


class ArgumentsField(Field):
    def __init__(self, required=False, nullable=False):
        super(ArgumentsField, self).__init__(required, nullable)
        self.basetype = dict

    def check_value(self, value):
        return isinstance(value, self.basetype)


class EmailField(CharField):
    def __init__(self, required=False, nullable=False):
        super(EmailField, self).__init__(required, nullable)
        self.pattern = r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+\.\w+$'

    def check_value(self, value):
        return super(EmailField, self).check_value(value)


class PhoneField(Field):
    def __init__(self, required=False, nullable=False):
        super(PhoneField, self).__init__(required, nullable)
        self.pattern = r'^7[0-9]{10}$'
        self.basetype = (basestring, int)

    def check_value(self, value):
        return super(PhoneField, self).check_value(value)


class DateField(Field):
    def __init__(self, required=False, nullable=False):
        super(DateField, self).__init__(required, nullable)
        self.pattern = "%d.%m.%Y"

    def __set__(self, instance, value):
        super(DateField, self).__set__(instance, value)

    def check_value(self, value):
        if isinstance(value, self.basetype):
            try:
                converted_date = datetime.datetime.strptime(value, self.pattern)
            except ValueError:
                return False
            return converted_date
        return False


class BirthDayField(DateField):
    def __init__(self, required=False, nullable=False):
        super(BirthDayField, self).__init__(required, nullable)
        self.max_age = 70

    def check_value(self, value):
        converted_date = super(BirthDayField, self).check_value(value)
        if converted_date and value:
            delta = datetime.datetime.today() - converted_date
            if delta.days < self.max_age * 365:
                return True


class GenderField(Field):
    def __init__(self, required=False, nullable=False):
        super(GenderField, self).__init__(required, nullable)
        self.pattern = r'^[012]{1}$'
        self.basetype = int

    def check_value(self, value):
        return super(GenderField, self).check_value(value)


class ClientIDsField(Field):
    def __init__(self, required=False, nullable=False):
        super(ClientIDsField, self).__init__(required, nullable)
        self.basetype = list

    def check_value(self, value):
        if isinstance(value, self.basetype) and len(value) > 0:
            for i in value:
                if not isinstance(i, int):
                    return False
            return True


class ModelMeta(type):
    """Метакласс позволит нам добавить имена полей Field внутрь объектов"""

    def __new__(mcls, name, bases, attrs):
        declared_fields = list()
        for attrname, attrvalue in attrs.iteritems():
            if isinstance(attrvalue, Field):
                attrvalue.name = attrname
                declared_fields.append(attrname)
        attrs["declared_fields"] = declared_fields
        return super(ModelMeta, mcls).__new__(mcls, name, bases, attrs)


class Model(object):
    """
    Базовый класс для моделей. Для создания принимает на вход объект-словарь.
    """
    __metaclass__ = ModelMeta

    def __init__(self, arguments=None):
        cls = self.__class__

        # Если задан аргумент при создании объекта, то будем использовать свою магию для проверки полей.
        if isinstance(arguments, dict):
            self.errors = {}

            # Зададим значения полей в нашем объекте, которые указаны в arguments и совпадают с полями класса.
            for key, value in arguments.iteritems():
                if key in cls.declared_fields:
                    try:
                        setattr(self, key, value)
                    except ValidationError, error:
                        self.errors[key] = error.message
                else:
                    self.errors[key] = u"Field with name {} are not declared in this object".format(key)

            for unused_field in set(cls.declared_fields) - set(arguments.keys()):
                # Если остальные поля не указаны, но нужны, то запишем ошибку аналогичную ошибкам ValidationError
                if getattr(cls, unused_field).required:
                    self.errors[unused_field] = u'Field {} are required, but value is None'.format(unused_field)
        else:
            raise ValidationError(
                u"Arguments for {} must have a dict type. We have '{}'".format(cls.__name__, type(arguments)))

    def is_valid(self):
        if hasattr(self, "errors") and len(self.errors) > 0:
            return False
        elif not hasattr(self, "errors"):
            # Тут можно проверить только required поля и "ненулевые" поля
            errors = dict()
            for field in self.declared_fields:
                value = getattr(self, field)
                if value is None and getattr(self.__class__, field).required is True:
                    errors[field] = u'Field {} are required, but value is None'.format(field)
                elif not getattr(self, field).check_nullable(value):
                    errors[field] = u'Field {} are not nullable, but value is None'.format(field)

            if len(errors) > 0:
                self.errors = errors
                return False
            else:
                return True
        else:
            return True

    def get_filled_fields(self):
        filled_fields = []
        for key, value in self.__class__.__dict__.iteritems():
            # Выясним какие поля есть в родительском классе являются типом Fields
            if isinstance(value, Field):
                # Далее проверим в экземпляре класса чему равен этот элемент, если не пуст, то добавим в filled_fields
                if getattr(self, key) is not None:
                    filled_fields.append(key)

        return filled_fields
