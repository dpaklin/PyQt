"""Модуль дескриптора серверного сокета."""

import logging
import sys

LOGGER = logging.getLogger('server')


class Port:
    """Класс-дескриптор контролирующий параметры порта сокета."""

    def __get__(self, instance, owner):
        """Возвращает значение аргумента."""
        return instance.__dict__[self.attr]

    def __set__(self, instance, value):
        """Присваивает значение аргументу."""
        if not 1024 <= value <= 65535:
            LOGGER.critical(f'Значение порта должно лежать в диапазоне 1024 - 65535.\n'
                            f'Значение {value} вне допустимого диапазона!')
            sys.exit(1)
        instance.__dict__[self.attr] = value

    def __set_name__(self, owner, attr):
        self.attr = attr
