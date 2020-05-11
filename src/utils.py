from urllib.parse import SplitResult
from urllib.parse import urlsplit


def base_host(r: SplitResult) -> str:
    # Интересует только основной домен, остальное игнорируем.
    # ``https://xxx.yyy.yandex.ru/search/`` тоже будет валидным.
    host = r.netloc.split('.')[-2:]
    host = '.'.join(host)
    return host


def is_organic_referer(url: str) -> bool:
    """ Можно ли считать данный узел ограническим переходом?
    """
    organic_hosts = {
        'yandex.ru',
        'google.com',
    }
    r = urlsplit(url=url)
    host = base_host(r=r)
    return host in organic_hosts


def is_success_finish(url: str) -> bool:
    """ Можно ли считать данный узел успехом? (покупкой)
        Сделаем допущение что домен у нас один, а успешных урлов у него может быть много
    """
    host = 'shop.com'
    locations = {
        '/checkout',
    }
    r = urlsplit(url=url)
    return r.netloc == host and r.path in locations


def is_cash_back_service(url: str) -> (bool, bool):
    """ Является ли данный узел переходом из кешбек-сервиса?
        А является ли этот кешбек-сервис нашим?
    """
    all_hosts = {
        'ours.com',
        'theirs1.com',
        'theirs2.com',
    }
    our_hosts = {
        'ours.com',
    }
    r = urlsplit(url=url)
    host = base_host(r=r)

    is_cash = host in all_hosts
    is_our = host in our_hosts and is_cash
    return is_cash, is_our
