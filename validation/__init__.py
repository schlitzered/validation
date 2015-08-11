__author__ = 'schlitzer'

import re
import socket
import uuid


class ValidationError(Exception):
    pass


class Base(object):
    def validate(self, item):
        raise NotImplementedError


class BaseNumber(Base):
    def __init__(self, typenum, typename, minval, maxval):
        self._typenum = typenum
        self._typename = typename
        if minval and type(minval) is not self._typenum:
            raise ValueError('minval is not an {0}'.format(self._typename))
        if maxval and type(maxval) is not self._typenum:
            raise ValueError('maxval is not an {0}'.format(self._typename))
        if minval and maxval:
            if minval > maxval:
                raise ValueError('min value bigger then max value')
        self._minval = minval
        self._maxval = maxval

    def validate(self, item):
        """

        :return: None, ValidationError
        """
        if type(item) is not self._typenum:
            raise ValidationError('{0} is not a {1}'.format(item, self._typename))
        if self._minval is not None:
            if self._minval > item:
                raise ValidationError('{0} is smaller then minimum value {1}'.format(item, self._minval))
        if self._maxval is not None:
            if self._maxval < item:
                raise ValidationError('{0} is bigger then maximum value {1}'.format(item, self._maxval))


class Bool(Base):
    """ Validate that item is a boolean

    """
    def validate(self, item):
        """Validate Item

        :return: None, ValidationError
        """
        if type(item) is not bool:
            raise ValidationError('{0} is not a boolean'.format(item))


class Choice(Base):
    """ Validate that item is a valid choice

    :param choices: List of allowed choices
    """
    def __init__(self, choices):
        self._choices = choices

    def validate(self, item):
        """ Validate that item is in the list of valid choices

        :return: None, ValidationError
        """
        if item not in self._choices:
            raise ValidationError("should be any of {0} actually is: {1}".format(self._choices, item))


class Dict(Base):
    """ Validate Dictionaries

    :param ignore_unknown: Boolean, indicating if unknown members should be ignored or not
    """
    def __init__(self, ignore_unknown=True):
        self._req_mem = {}
        self._opt_mem = {}
        self._ignore = ignore_unknown

    @property
    def required(self):
        """ Dictionary holding required members

        The value should be a instance of a Type Validator

        :return: dict with required members
        """
        return self._req_mem

    @property
    def optional(self):
        """ Dictionary holding optional members

        The value should be a instance of a Type Validator

        :return: dict with optional members
        """
        return self._opt_mem

    def validate(self, item):
        """ Validate Dictionary

        :return: None, ValidationError
        """
        if type(item) is not dict:
            raise ValidationError("is not a dictionary")
        keys = set(item.keys())

        for key, validator in self.required.items():
            try:
                validator.validate(item[key])
                keys.remove(key)
            except ValidationError as err:
                raise ValidationError("required member {0} {1}".format(key, err))
            except KeyError:
                raise ValidationError("required member {0} missing".format(key))

        for key, validator in self.optional.items():
            try:
                validator.validate(item[key])
                keys.remove(key)
            except ValidationError as err:
                raise ValidationError("optional member {0} {1}".format(key, err))
            except KeyError:
                pass

        if not self._ignore:
            if len(keys) > 0:
                raise ValidationError("got unknown members: {0}".format(keys))


class Float(BaseNumber):
    """ Validate Floats

    :param minval: Optional Minimum allowed value
    :param maxval: Optional Maximum allowed value
    """
    def __init__(self, minval=None, maxval=None):
        super().__init__(typenum=float, typename='float', minval=minval, maxval=maxval)


class Int(BaseNumber):
    """ Validate Integers

    :param minval: Optional Minimum allowed value
    :param maxval: Optional Maximum allowed value
    """
    def __init__(self, minval=None, maxval=None):
        super().__init__(typenum=int, typename='integer', minval=minval, maxval=maxval)


class IP(Base):
    """ Validate if item is a valid IPv4 or IPv6 address

    """
    def __init__(self):
        self._ipv4 = IPv4()
        self._ipv6 = IPv6()

    def validate(self, item):
        """ Validate IP

        :return: None, ValidationError
        """
        try:
            self._ipv4.validate(item)
        except ValidationError:
            try:
                self._ipv6.validate(item)
            except ValidationError:
                raise ValidationError("not a IPv4 or IPv6 address")


class IPPort(Base):
    """ Validate if item is a valid IPv4 or IPv6 address with Port

    """
    def __init__(self):
        self._port = Int(minval=1, maxval=65535)
        self._ip = IP()

    def validate(self, item):
        """ Validate IP:Port

        :return: None, ValidationError
        """
        ip, port = item.rsplit(':', 1)
        self._ip.validate(ip)
        try:
            self._port.validate(int(port))
        except ValidationError:
            raise ValidationError("port outside valid range")


class IPv4(Base):
    """ Validate that IPv4 addresses

    """
    def validate(self, item):
        """ Validate IP

        :return: None, ValidationError
        """
        try:
            socket.inet_pton(socket.AF_INET, item)
        except (socket.gaierror, OSError):
            raise ValidationError('not a IPv4 address')


class IPv4Port(Base):
    def __init__(self):
        self._port = Int(minval=1, maxval=65535)
        self._ip = IPv4()

    def validate(self, item):
        """ Validate IP:Port

        :return: None, ValidationError
        """
        ip, port = item.rsplit(':', 1)
        self._ip.validate(ip)
        try:
            self._port.validate(int(port))
        except ValidationError:
            raise ValidationError("port outside valid range")


class IPv6(Base):
    """ Validate IPv6 Addresses

    """
    def __init__(self):
        self._port = Int(minval=1, maxval=65535)

    def validate(self, item):
        """ Validate IP

        :return: None, ValidationError
        """
        try:
            socket.inet_pton(socket.AF_INET6, item)
        except (socket.gaierror, OSError):
            raise ValidationError('not a IPv6 address')


class IPv6Port(Base):
    def __init__(self):
        self._port = Int(minval=1, maxval=65535)
        self._ip = IPv6()

    def validate(self, item):
        """ Validate IP:Port

        :return: None, ValidationError
        """
        ip, port = item.rsplit(':', 1)
        self._ip.validate(ip)
        try:
            self._port.validate(int(port))
        except ValidationError:
            raise ValidationError("port outside valid range")


class List(Base):
    """ Validate that all members of the list are from the same type

    :parem validator: A Type Validator Instance
    """
    def __init__(self, validator=None):
        self._validator = validator

    @property
    def validator(self):
        """ The Type Validator that is used

        :return: Type Validator Instance
        """
        return self._validator

    @validator.setter
    def validator(self, value):
        self._validator = value

    def validate(self, item):
        """

        :return: None, ValidationError
        """
        length = len(item)
        for pos in range(length):
            try:
                self.validator.validate(item[pos])
            except ValidationError as err:
                raise ValidationError("list position [{0}] {1}".format(pos, err))


class String(Base):
    """ Validate String

    :param regex: Optional Regex that is used to validate the string
    """
    def __init__(self, regex=None):
        self._regex = None
        self.regex = regex

    @property
    def regex(self):
        """ Regex to check the string against

        :return: regex instance
        """
        return self._regex

    @regex.setter
    def regex(self, value):
        if value is None:
            self._regex = None
        else:
            self._regex = re.compile(value)

    def validate(self, item):
        """ Validate String

        :return: None, ValidationError
        """
        if type(item) is not str:
            raise ValidationError('is not a string')
        if self.regex:
            if not self.regex.match(item):
                raise ValidationError('string: {0} not matching pattern: {1}'.format(item, self._regex.pattern))


class StringUUID(Base):
    """ Validate that string is a valid UUID

    """
    def validate(self, item):
        """ Validate UUID

        :return: None, ValidationError
        """
        try:
            uuid.UUID(item)
        except (ValueError, AttributeError):
            raise ValidationError("{0} is not a uuid".format(item))


class Tuple(Base):
    """ Check fixes size list/tuple against different Type Validators

    """
    def __init__(self):
        self._elements = []

    @property
    def elements(self):
        """

        :return: List of Type Validators that represent the structure of the tuple/list
        """
        return self._elements

    def add_element(self, validator):
        """ Append new element to the tuple

        :param validator: Type Validator Instance
        """
        self._elements.append(validator)

    def validate(self, item):
        """ Validate the tuple/list

        :return: None, ValidationError
        """
        length = len(self.elements)
        len_item = len(item)
        if length != len_item:
            raise ValidationError("unexpected length, expected {0} but is {1}".format(length, len_item))
        for element in range(length):
            try:
                self.elements[element].validate(item[element])
            except ValidationError as err:
                raise ValidationError("[{0}]{1}".format(element, err))
