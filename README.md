Резюме (что было сделано)
-------------------------

Алгоритм работы:

* Прочитать целиком входной файл;
* Выкинуть все огранические переходы (раз они ни на что не влияют);
* Сгруппировать события по юзерам, отсортировать по дате;
* Пройтись по каждому полученному юзеру;
* Если его последнее событие -- не успешная покупка, то выкинуть такого юзера. Тут используется допущение
  что логи уже чистые и подготовленные (судя по предоставленным данным и таймингу 1 час). В реальном мире
  нужно искать несколько покупок у каждого пользователя, и для каждой покупки повторять описанные ниже действия;
* В обратном порядке (от новых к старым) пройтись по событиям и найти первый переход из кешбек-сервиса;
* Если это наш сервис, то успех (сохранить юзера в отдельный файл), если не наш, то нафиг.


Установка
---------

Требования:
* Используется **Python 3.8.**
* Не требует внешних зависимостей для использования.
* Для запуска юнит-тестов потребуются дополнительные зависимости:
    ```
    python3.8 -m venv .venv
    source .venv/bin/activate
    pip install -r pip-requirements-dev.txt
    ```

(Код совместим с более ранними версиями вплоть до 3.5, но зависимости для юнит-тестов - нет,
нужно поискать более старую версию coverage.)


Запустить юнит-тесты (без подсчёта покрытия):
```
make test
```

Запустить юнит-тесты (с подсчётом покрытия) и построить отчёт:
```
make coverage
make coverage_report
```


Как пользоваться
----------------

Посмотреть все опции:
```
python src/main.py -h
```

Пример запуска:
```
python src/main.py -p src/tests/fixture1.json --log-level DEBUG
```

[Пример результата](reports/report-1589152103.txt)


Условие задания от заказчика
----------------------------

Пользователи посещают сайт магазина **Shop**. Они могут приходить из поисковиков (органический трафик),
приходить по партнерским ссылкам нескольких кэшбек-сервисов: нашего (**Ours**) и других (**Theirs1**, **Theirs2**).

Примеры логов в БД сервиса **Ours**, которые собираются скриптом со всех страниц сайта магазина:

1) Органический переход клиента в магазин
```json
[
    {
        "client_id": "user15",
        "User-Agent": "Firefox 59",
        "document.location": "https://shop.com/products/?id=2",
        "document.referer": "https://yandex.ru/search/?q=купить+котика",
        "date": "2018-04-03T07:59:13.286000Z"
    }
]
```

2) Переход клиента в магазин по партнерской ссылке кэшбек-сервиса
```json
[
    {
        "client_id": "user15",
        "User-Agent": "Firefox 59",
        "document.location": "https://shop.com/products/?id=2",
        "document.referer": "https://referal.ours.com/?ref=123hexcode",
        "date": "2018-04-04T08:30:14.104000Z"
    },
    {
        "client_id": "user15",
        "User-Agent": "Firefox 59",
        "document.location": "https://shop.com/products/?id=2",
        "document.referer": "https://ad.theirs1.com/?src=q1w2e3r4",
        "date": "2018-04-04T08:45:14.384000Z"
    }
]
```

3) Внутренний переход клиента в магазине
```json
[
    {
        "client_id": "user15",
        "User-Agent": "Firefox 59",
        "document.location": "https://shop.com/checkout",
        "document.referer": "https://shop.com/products/?id=2",
        "date": "2018-04-04T08:59:16.222000Z"
    }
]
```

Магазин **Shop** платит кэшбек-сервисам за клиентов, которые перешли по их ссылке,
оплатили товар и в конце попали на страницу https://shop.com/checkout ("Спасибо за заказ").
Комиссия выплачивается по принципу "выигрывает последний кэшбек-сервис,
после перехода по партнерской ссылке которого клиент купил товар".

Сервис **Ours** хочет по своим логам находить клиентов, которые совершили покупку именно благодаря ему.
Нужно написать программу, которая ищет победившие партнерские ссылки сервиса **Ours**.
Учесть различные сценарии поведения клиента на сайте.

На выходе менеджер ожидает получить список клиентов и какие партнерские ссылки привели к их покупкам.

Будет плюсом​, если будут предоставлены доказательства правильности работы алгоритма.

Решение прислать в виде ссылки на код проекта на https://github.com/. В репозитории разместить файл README.md, содержащий пошаговую инструкцию по развертыванию и использованию проекта.

Дополнительно примеры логов:
```json
[
    {
        "client_id": "user7",
        "User-Agent": "Chrome 65",
        "document.location": "https://shop.com/",
        "document.referer": "https://referal.ours.com/?ref=0xc0ffee",
        "date": "2018-05-23T18:59:13.286000Z"
    },
    {
        "client_id": "user7",
        "User-Agent": "Chrome 65",
        "document.location": "https://shop.com/products/?id=10",
        "document.referer": "https://shop.com/",
        "date": "2018-05-23T18:59:20.119000Z"
    },
    {
        "client_id": "user7",
        "User-Agent": "Chrome 65",
        "document.location": "https://shop.com/products/?id=25",
        "document.referer": "https://shop.com/products/?id=10",
        "date": "2018-05-23T19:04:20.119000Z"
    },
    {
        "client_id": "user7",
        "User-Agent": "Chrome 65",
        "document.location": "https://shop.com/cart",
        "document.referer": "https://shop.com/products/?id=25",
        "date": "2018-05-23T19:05:13.123000Z"
    },
    {
        "client_id": "user7",
        "User-Agent": "Chrome 65",
        "document.location": "https://shop.com/checkout",
        "document.referer": "https://shop.com/cart",
        "date": "2018-05-23T19:05:59.224000Z"
    }
]
```
