import unittest
from urllib.parse import urlsplit

from src.utils import base_host
from src.utils import is_organic_referer
from src.utils import is_success_finish
from src.utils import is_cash_back_service


class FunctionsTestCase(unittest.TestCase):

    def test_base_host(self):
        r = urlsplit('https://xxx.yyy.yandex.ru/search/')
        self.assertEqual(base_host(r=r), 'yandex.ru')

        r = urlsplit('https://cashback.ooo/search/?ref=1')
        self.assertEqual(base_host(r=r), 'cashback.ooo')

    def test_is_organic_referer(self):
        url = 'https://xxx.yyy.yandex.ru/search/'
        self.assertTrue(is_organic_referer(url=url))

        url = 'http://google.com/'
        self.assertTrue(is_organic_referer(url=url))

        url = 'https://goo.gl/kek?ref=1'
        self.assertFalse(is_organic_referer(url=url))

    def test_is_success_finish(self):
        url = 'https://shop.com/checkout'
        self.assertTrue(is_success_finish(url=url))

        url = 'http://shop.com/checkout'
        self.assertTrue(is_success_finish(url=url))

        url = 'http://xxx.shop.com/checkout'
        self.assertFalse(is_success_finish(url=url))

    def test_is_cash_back_service(self):
        url = 'https://shop.com/checkout'
        self.assertEqual(is_cash_back_service(url=url), (False, False))

        url = 'https://referal.ours.com/?ref=123hexcode'
        self.assertEqual(is_cash_back_service(url=url), (True, True))

        url = 'https://ad.theirs1.com/?src=q1w2e3r4'
        self.assertEqual(is_cash_back_service(url=url), (True, False))

        url = 'https://ad.theirs2.com/?src=q1w2e3r4'
        self.assertEqual(is_cash_back_service(url=url), (True, False))
