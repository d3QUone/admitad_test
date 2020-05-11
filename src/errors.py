class ParserException(Exception):
    """Базовое исключение"""


class BadDataException(ParserException):
    """Полученные данные имеют невалидный формат"""
