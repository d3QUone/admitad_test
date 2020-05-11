import argparse
import collections
import json
import logging
import logging.handlers
import os
import sys
import time
import typing

from src.errors import ParserException
from src.errors import BadDataException
from src.utils import is_organic_referer
from src.utils import is_success_finish
from src.utils import is_cash_back_service


logger = logging.getLogger(__name__)
success_logger = logging.getLogger('report')

BASE_PATH = os.path.dirname(os.path.dirname(__file__))


ParseItem = collections.namedtuple(
    'ParseItem',
    (
        'client_id',
        'user_agent',
        'location',
        'referer',
        'date',
    )
)


def load_file(path: str, ignore_invalid_items: bool = False) -> typing.List[ParseItem]:
    """ Прочитать содержимое файла и вернуть готовый объект

    :param path: путь до файла
    :param ignore_invalid_items: пропускать ли невалидные записи в логе или падать на них
    """
    if not os.path.exists(path) or not os.path.isfile(path):
        logger.error('Файл не найден: %s', path)
        raise ParserException
    with open(path) as f:
        r = json.load(f)

    if not isinstance(r, list):
        logger.error('В логе ожидается список объектов')
        raise BadDataException

    res = []
    for item in r:
        client_id = item.get('client_id')
        user_agent = item.get('User-Agent')
        location = item.get('document.location')
        referer = item.get('document.referer')
        date = item.get('date')

        # TODO: тут надо добавить больше валидации, но мне лень

        if not all([client_id, user_agent, location, referer, date]):
            if not ignore_invalid_items:
                logger.error('Невалидная запись: %s', item)
                raise BadDataException
            continue

        # Тут же можно выкинуть ненужные записи, например ``https://yandex.ru/search/``
        if is_organic_referer(url=referer):
            continue

        res.append(ParseItem(
            client_id=client_id,
            user_agent=user_agent,
            location=location,
            referer=referer,
            date=date,
        ))

    return res


def parse_data(data: typing.List[ParseItem]) -> typing.List[ParseItem]:
    # Сгруппировать данные по пользователям
    clients = collections.defaultdict(list)
    for item in data:
        clients[item.client_id].append(item)
    logger.debug('Найдена история %s клиентов', len(clients))

    # Для каждого пользователя найти последнюю транзакцию
    res = []
    for client, history in clients.items():
        logger.debug('Client: %s', client)
        history = sorted(history, key=lambda ii: ii.date, reverse=True)

        # Если последняя точка не корзина, то нафиг. Хотя в общем случае более правильно
        # дробить весь список на несколько покупок, т.к. может оказаться что первая уже
        # завершена, а вторая ещё только в процессе.
        if not is_success_finish(history[0].location):
            logger.debug('Последнее событие -- не покупка')
            continue

        # Пройтись в обратном порядке пока не найдём первый переход из кешбек-сервиса. Повезёт если он наш.
        for i in history:
            logger.debug('>> %s', i)
            is_cash, is_our = is_cash_back_service(url=i.referer)
            if is_cash:
                if is_our:
                    logger.info('Наш клиент: %s, %s', client, i.referer)
                    success_logger.info('Наш клиент: %s, %s', client, i.referer)
                    res.append(i)
                else:
                    logger.debug('Не наш клиент: %s, %s', client, i.referer)
                break
    return res


def main(log_file_path: str, ignore_invalid_items: bool = False):
    data = load_file(
        path=log_file_path,
        ignore_invalid_items=ignore_invalid_items,
    )
    if not data:
        logger.info('Пустой файл')
        return

    parse_data(data=data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Скрипт для парсинга логов Admitad',
    )
    parser.add_argument(
        '-p',
        required=True,
        type=str,
        dest='log_file_path',
        help=u'Путь до файла с логами, который будет парситься',
    )
    parser.add_argument(
        '-i',
        default=False,
        action='store_true',
        dest='ignore_invalid_items',
        help=u'Пропускать ли невалидные записи в логе или падать на них',
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        type=str,
        dest='log_level',
        choices=['DEBUG', 'INFO', 'WARNINGS', 'ERROR'],
        help=u'Уровень логирования',
    )
    args = parser.parse_args()

    # Настроить логирование
    # TODO: в идеале вынести в dictConfig, но это простой скрипт, так что пофиг
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(message)s',
    )

    # В стандартный вывод печатать всё
    level = getattr(logging, args.log_level, logging.INFO)
    stdout = logging.StreamHandler(
        stream=sys.stdout,
    )
    stdout.setLevel(level)
    stdout.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(stdout)

    # А в файлик печатать только результаты
    fn = os.path.join(BASE_PATH, 'reports', 'report-{}.txt'.format(int(time.time())))
    logger.info('Результаты будут сохранены в файле: %s', fn)
    report = logging.handlers.WatchedFileHandler(
        filename=fn,
    )
    report.setLevel(logging.INFO)
    report.setFormatter(formatter)

    success_logger.setLevel(logging.INFO)
    success_logger.addHandler(report)

    # Поехали
    main(
        log_file_path=args.log_file_path,
        ignore_invalid_items=args.ignore_invalid_items,
    )

