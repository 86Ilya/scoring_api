# -*- coding: utf-8 -*-

import re
import datetime
import abc


class Field(object):
    """Базовый класс определяющий поле. От него наследуются все другие поля."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable
        self.values_keeper = dict()
        self.pattern = None
        self.basetype = basestring
        self.name = None

    def __set__(self, instance, value):
        if instance:
            if self.check_value(value):
                self.values_keeper[instance] = value
            else:
                raise ValueError(
                    u'Field {} are not compatible with value "{}" type "{}"'.format(self.name, value,
                                                                                    type(value).__name__))

    def __get__(self, instance, owner):
        if instance:
            return self.values_keeper.get(instance, None)
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
        if value is None and self.nullable:
            return True
        else:
            return False


class CharField(Field):
    def __init__(self, required=False, nullable=False):
        super(CharField, self).__init__(required, nullable)
        self.pattern = r'(.){0,256}'

    def check_value(self, value):
        if self.check_nullable(value):
            return True
        else:
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
        self.pattern = r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    def check_value(self, value):
        if self.check_nullable(value):
            return True
        else:
            return super(EmailField, self).check_value(value)


class PhoneField(Field):
    def __init__(self, required=False, nullable=False):
        super(PhoneField, self).__init__(required, nullable)
        self.pattern = r'^7[0-9]{10}$'
        self.basetype = (basestring, int)

    def check_value(self, value):
        if self.check_nullable(value):
            return True
        else:
            return super(PhoneField, self).check_value(value)


class DateField(Field):
    def __init__(self, required=False, nullable=False):
        super(DateField, self).__init__(required, nullable)
        self.pattern = "%d.%m.%Y"

    def __set__(self, instance, value):
        super(DateField, self).__set__(instance, value)

    def check_value(self, value):
        if self.check_nullable(value):
            return True
        elif isinstance(value, self.basetype):
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
        if self.check_nullable(value):
            return True
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
        if self.check_nullable(value):
            return True
        else:
            return super(GenderField, self).check_value(value)


class ClientIDsField(Field):
    def __init__(self, required=False, nullable=False):
        super(ClientIDsField, self).__init__(required, nullable)
        self.basetype = list

    def check_value(self, value):
        if self.check_nullable(value):
            return True
        elif isinstance(value, self.basetype) and len(value) > 0:
            for i in value:
                if not isinstance(i, int):
                    return False
            return True


class ModelMeta(type):
    """Метакласс позволит нам добавить имена полей Field внутрь объектов"""
    def __new__(mcls, name, bases, attrs):
        for attrname, attrvalue in attrs.iteritems():
            if isinstance(attrvalue, Field):
                attrvalue.name = attrname
        return super(ModelMeta, mcls).__new__(mcls, name, bases, attrs)


class Model(object):
    __metaclass__ = ModelMeta

    def get_filled_fields(self):
        filled_fields = []
        for key, value in self.__class__.__dict__.iteritems():
            # Выясним какие поля есть в родительском классе являются типом Fields
            if isinstance(value, Field):
                # Далее проверим в экземпляре класса чему равен этот элемент, если не пуст, то добавим в filled_fields
                if getattr(self, key) is not None:
                    filled_fields.append(key)

        return filled_fields
