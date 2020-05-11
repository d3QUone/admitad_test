import os
import unittest

from src.errors import BadDataException
from src.errors import ParserException
from src.main import load_file
from src.main import parse_data
from src.main import ParseItem
from src.main import BASE_PATH


BASE_PATH = os.path.join(BASE_PATH, 'src', 'tests')


class ParserTestCase(unittest.TestCase):

    def assert_is_parse_item(self, item):
        self.assertIsInstance(item, ParseItem)

    def test_load_file_does_not_exists(self):
        with self.assertRaises(ParserException):
            load_file(path='xxx.unknown.yyy')

    def test_load_bad_file(self):
        path = os.path.join(BASE_PATH, 'fixture2.json')
        with self.assertRaises(BadDataException):
            load_file(path=path)

    def test_load_good_file(self):
        path = os.path.join(BASE_PATH, 'fixture1.json')
        r = load_file(path=path)
        # вообще записей 9, но 1 из них ограника
        self.assertEqual(len(r), 8)
        for i in r:
            self.assert_is_parse_item(item=i)

    def test_load_corrupted_data(self):
        # Есть невалидные данные
        path = os.path.join(BASE_PATH, 'fixture3.json')
        with self.assertRaises(BadDataException):
            load_file(path=path, ignore_invalid_items=False)

        # Но можем их игнорировать
        r = load_file(path=path, ignore_invalid_items=True)
        self.assertEqual(len(r), 1)
        for i in r:
            self.assert_is_parse_item(item=i)

    def test_two_customers(self):
        path = os.path.join(BASE_PATH, 'fixture1.json')
        data = load_file(path=path)

        r = parse_data(data=data)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].client_id, 'user7')
        self.assertEqual(r[0].referer, 'https://referal.ours.com/?ref=0xc0ffee')

    def test_no_customers(self):
        path = os.path.join(BASE_PATH, 'fixture1.json')
        data = load_file(path=path)[:2]

        r = parse_data(data=data)
        self.assertEqual(len(r), 0)
