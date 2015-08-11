__author__ = 'schlitzer'

from unittest import TestCase
from unittest.mock import Mock, patch

import validation


class TestBase(TestCase):
    def test_validate_NotImplemented(self):
        base = validation.Base()
        self.assertRaises(NotImplementedError, base.validate, None)


class TestBaseNumber(TestCase):
    def test___init__(self):
        basenumber = validation.BaseNumber(int, 'integer', 0, 100)
        self.assertEqual(basenumber._typenum, int)
        self.assertEqual(basenumber._typename, 'integer')
        self.assertEqual(basenumber._minval, 0)
        self.assertEqual(basenumber._maxval, 100)

    def test___init__min_bigger_them_max(self):
        self.assertRaises(ValueError, validation.BaseNumber, int, 'integer', 200, 100)

    def test___init__min_wrong_type(self):
        self.assertRaises(ValueError, validation.BaseNumber, int, 'integer', 0.200, 100)

    def test___init__max_wrong_type(self):
        self.assertRaises(ValueError, validation.BaseNumber, int, 'integer', 0, 0.100)

    def test_validate(self):
        basenumber = validation.BaseNumber(int, 'integer', None, None)
        self.assertIsNone(basenumber.validate(10))

    def test_validate_range(self):
        basenumber = validation.BaseNumber(int, 'integer', 0, 100)
        self.assertIsNone(basenumber.validate(10))

    def test_validate_to_small(self):
        basenumber = validation.BaseNumber(int, 'integer', 0, 100)
        self.assertRaises(validation.ValidationError, basenumber.validate, -1)

    def test_validate_to_big(self):
        basenumber = validation.BaseNumber(int, 'integer', 0, 100)
        self.assertRaises(validation.ValidationError, basenumber.validate, 101)

    def test_validate_no_int(self):
        basenumber = validation.BaseNumber(int, 'integer', 0, 100)
        self.assertRaises(validation.ValidationError, basenumber.validate, 0.1)


class TestBool(TestCase):
    def test_true(self):
        booltype = validation.Bool()
        booltype.validate(True)

    def test_False(self):
        booltype = validation.Bool()
        booltype.validate(False)

    def test_non_bool(self):
        booltype = validation.Bool()
        self.assertRaises(validation.ValidationError, booltype.validate, 'blarg')


class TestChoice(TestCase):
    def test_validate(self):
        choicetype = validation.Choice(choices=['yes', 'no'])
        self.assertIsNone(choicetype.validate('no'))

    def test_validate_invalid(self):
        choicetype = validation.Choice(choices=['yes', 'no'])
        self.assertRaises(validation.ValidationError, choicetype.validate, 'blarg')


class TestDict(TestCase):
    def test___init__(self):
        dicttype = validation.Dict(ignore_unknown=False)
        self.assertEquals(dicttype.required, {})
        self.assertEquals(dicttype.optional, {})
        self.assertFalse(dicttype._ignore)

    def test_required_ok(self):
        candidate = {
            'attr1': True,
            'attr2': False
        }

        dicttype = validation.Dict()
        dicttype.required['attr1'] = validation.Bool()
        dicttype.required['attr2'] = validation.Bool()

        self.assertIsNone(dicttype.validate(candidate))

    def test_required_not_ok(self):
        candidate = {
            'attr1': True,
            'attr2': 42
        }

        dicttype = validation.Dict()
        dicttype.required['attr1'] = validation.Bool()
        dicttype.required['attr2'] = validation.Bool()

        self.assertRaises(validation.ValidationError, dicttype.validate, candidate)

    def test_required_missing(self):
        candidate = {
            'attr1': True
        }

        dicttype = validation.Dict()
        dicttype.required['attr1'] = validation.Bool()
        dicttype.required['attr2'] = validation.Bool()

        self.assertRaises(validation.ValidationError, dicttype.validate, candidate)

    def test_optional_ok(self):
        candidate = {
            'attr1': True,
            'attr2': False
        }

        dicttype = validation.Dict()
        dicttype.optional['attr1'] = validation.Bool()
        dicttype.optional['attr2'] = validation.Bool()

        self.assertIsNone(dicttype.validate(candidate))

    def test_optional_not_ok(self):
        candidate = {
            'attr1': True,
            'attr2': 42
        }

        dicttype = validation.Dict()
        dicttype.optional['attr1'] = validation.Bool()
        dicttype.optional['attr2'] = validation.Bool()

        self.assertRaises(validation.ValidationError, dicttype.validate, candidate)

    def test_ignore_unknown_true(self):
        candidate = {
            'attr1': True,
            'attr2': False
        }

        dicttype = validation.Dict()
        self.assertIsNone(dicttype.validate(candidate))

    def test_ignore_unknown_false(self):
        candidate = {
            'attr1': True,
            'attr2': False,
        }

        dicttype = validation.Dict(ignore_unknown=False)
        self.assertRaises(validation.ValidationError, dicttype.validate, candidate)


class TestFloat(TestCase):
    def test___init__(self):
        floattype = validation.Float()
        self.assertEqual(floattype._typenum, float)
        self.assertEqual(floattype._typename, 'float')


class TestInt(TestCase):
    def test___init__(self):
        inttype = validation.Int()
        self.assertEqual(inttype._typenum, int)
        self.assertEqual(inttype._typename, 'integer')


class TestIP(TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)

        ipv4_patcher = patch('validation.IPv4')
        self.ipv4_mock = ipv4_patcher.start()
        self.ipv4 = Mock()
        self.ipv4_mock.return_value = self.ipv4

        ipv6_patcher = patch('validation.IPv6')
        self.ipv6_mock = ipv6_patcher.start()
        self.ipv6 = Mock()
        self.ipv6_mock.return_value = self.ipv6

    def test_validate_ipv4_ok(self):
        iptype = validation.IP()

        self.ipv4.validate.return_value = None
        self.ipv6.validate.side_effect = validation.ValidationError()

        self.assertIsNone(iptype.validate('127.0.0.1'))

    def test_validate_ipv6_ok(self):
        iptype = validation.IP()

        self.ipv6.validate.return_value = None
        self.ipv4.validate.side_effect = validation.ValidationError()

        self.assertIsNone(iptype.validate('::1'))

    def test_validate_no_ip(self):
        iptype = validation.IP()

        self.ipv6.validate.side_effect = validation.ValidationError()
        self.ipv4.validate.side_effect = validation.ValidationError()

        self.assertRaises(validation.ValidationError, iptype.validate, 'blarg')


class TestIPPort(TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)

        ip_patcher = patch('validation.IP')
        self.ip_mock = ip_patcher.start()
        self.ip = Mock()
        self.ip_mock.return_value = self.ip

        int_patcher = patch('validation.Int')
        self.int_mock = int_patcher.start()
        self.int = Mock()
        self.int_mock.return_value = self.int

    def test_validate(self):
        ipporttype = validation.IPPort()
        self.assertIsNone(ipporttype.validate('127.0.0.1:3128'))
        self.assertIsNone(ipporttype.validate('::1:3128'))

    def test_validate_port_wrong(self):
        ipporttype = validation.IPPort()

        self.int.validate.side_effect = validation.ValidationError()

        self.assertRaises(validation.ValidationError, ipporttype.validate, '127.0.0.1:83128')
        self.assertRaises(validation.ValidationError, ipporttype.validate, '::1:93128')

    def test_validate_ip_wrong(self):
        ipporttype = validation.IPPort()

        self.ip.validate.side_effect = validation.ValidationError()

        self.assertRaises(validation.ValidationError, ipporttype.validate, '123123127.0.0.1:3128')
        self.assertRaises(validation.ValidationError, ipporttype.validate, '123123123::1:3128')


class TestIPv4(TestCase):
    def test_validate_valid(self):
        ipv4type = validation.IPv4()
        self.assertIsNone(ipv4type.validate('127.0.0.1'))

    def test_validate_invalid(self):
        ipv4type = validation.IPv4()
        self.assertRaises(validation.ValidationError, ipv4type.validate, '256.0.0.1')


class TestIPv4Port(TestCase):
    def test_validate_valid(self):
        ipv4type = validation.IPv4Port()
        self.assertIsNone(ipv4type.validate('127.0.0.1:3128'))

    def test_validate_invalid_ip(self):
        ipv4type = validation.IPv4Port()
        self.assertRaises(validation.ValidationError, ipv4type.validate, '256.0.0.1:3128')

    def test_validate_invalid_port(self):
        ipv4type = validation.IPv4Port()
        self.assertRaises(validation.ValidationError, ipv4type.validate, '127.0.0.1:83128')


class TestIPv6(TestCase):
    def test_validate_valid(self):
        ipv6type = validation.IPv6()
        self.assertIsNone(ipv6type.validate('::1'))

    def test_validate_invalid(self):
        ipv6type = validation.IPv6()
        self.assertRaises(validation.ValidationError, ipv6type.validate, '::1k12')


class TestIPv6Port(TestCase):
    def test_validate_valid(self):
        ipv6type = validation.IPv6Port()
        self.assertIsNone(ipv6type.validate('::1:3128'))

    def test_validate_invalid_ip(self):
        ipv6type = validation.IPv6Port()
        self.assertRaises(validation.ValidationError, ipv6type.validate, '::1iasd:3128')

    def test_validate_invalid_port(self):
        ipv6type = validation.IPv6Port()
        self.assertRaises(validation.ValidationError, ipv6type.validate, '::1:83128')


class TestList(TestCase):
    def test_validate(self):
        listtype = validation.List()
        listtype.validator = validation.Bool()
        self.assertIsNone(listtype.validate([True, False, True]))

    def test_validate_invalid(self):
        listtype = validation.List()
        listtype.validator = validation.Bool()
        self.assertRaises(validation.ValidationError, listtype.validate, [True, False, None])


class TestString(TestCase):
    def test_validate_simple_string(self):
        stringtype = validation.String()
        self.assertIsNone(stringtype.validate('test test'))

    def test_validate_simple_string_regex(self):
        stringtype = validation.String(regex='^test.*')
        self.assertIsNone(stringtype.validate('test test'))

    def test_validate_simple_string_invalid(self):
        stringtype = validation.String()
        self.assertRaises(validation.ValidationError, stringtype.validate, 42)

    def test_validate_simple_string_regex_invalid(self):
        stringtype = validation.String(regex='^test.*')
        self.assertRaises(validation.ValidationError, stringtype.validate, 'blargtest test')


class TestStringUUID(TestCase):
    def test_validate_valid(self):
        stringuuidtype = validation.StringUUID()
        self.assertIsNone(stringuuidtype.validate('e7a5ff1c-ee5e-4ca9-a3d3-0106dd826dcd'))

    def test_validate_invalid(self):
        stringuuidtype = validation.StringUUID()
        self.assertRaises(validation.ValidationError, stringuuidtype.validate, 'e7a5ff1c-ee5e-4ca9-a3d3-0106ddblargd')


class TestTuple(TestCase):
    def test_validate(self):
        tupletype = validation.Tuple()
        tupletype.add_element(validation.Bool())
        tupletype.add_element(validation.Int())
        tupletype.add_element(validation.String())
        self.assertIsNone(tupletype.validate([True, 42, 'blarg']))

    def test_validate_invalid_member(self):
        tupletype = validation.Tuple()
        tupletype.add_element(validation.Bool())
        tupletype.add_element(validation.Int())
        tupletype.add_element(validation.String())
        self.assertRaises(validation.ValidationError, tupletype.validate, [True, False, 'blarg'])

    def test_validate_invalid_member_count(self):
        tupletype = validation.Tuple()
        tupletype.add_element(validation.Bool())
        tupletype.add_element(validation.Int())
        tupletype.add_element(validation.String())
        self.assertRaises(validation.ValidationError, tupletype.validate, [True, 42, 'blarg', None])
