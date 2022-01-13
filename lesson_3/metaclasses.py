"""Модуль, содержащий метаклассы клиентского и серверного классов."""

import dis
import logging


class ClientVerifier(type):
    """
    Метакласс, выполняющий базовую проверку класса Client на соответствие основным требованиям.
    Контролирует отсутствие вызовов accept и listen для сокетов,
    наличие использования сокетов для работы по TCP,
    отсутствие создания сокетов на уровне классов.
    """

    def __init__(cls, clsname, bases, clsdict):
        cls.logger = logging.getLogger('client')
        # Список атрибутов:
        attributes = []
        # Список используемых методов:
        methods = []

        # Проверка содержимого словаря:
        for key in clsdict:
            try:
                ret = dis.get_instructions(clsdict[key])
            # если не функция:
            except TypeError:
                pass
            # если функция:
            else:
                # получаем используемые методы и атрибуты:
                for i in ret:
                    if i.opname == 'LOAD_ATTR' and i.argval not in attributes:
                        attributes.append(i.argval)
                    elif i.opname == 'LOAD_GLOBAL' and i.argval not in methods:
                        methods.append(i.argval)

        # Проверка использования недопустимых методов:
        for func in ('accept', 'listen', 'socket'):
            if func in methods:
                cls.logger.error('Использованы методы "accept", "listen", "socket" при создании клиента.')
                raise TypeError('Методы "accept", "listen", "socket" не должны использоваться при создании клиента.')
        super().__init__(clsname, bases, clsdict)


class ServerVerifier(type):
    """
    Метакласс, выполняющий базовую проверку класса Server на соответствие основным требованиям.
    Контролирует отсутствие вызовов connect для сокетов,
    наличие использования сокетов для работы по TCP.
    """

    def __init__(cls, clsname, bases, clsdict):
        cls.logger = logging.getLogger('server')
        # Список атрибутов:
        attributes = []
        # Список используемых методов:
        methods = []

        # Проверка содержимого словаря:
        for key in clsdict:
            try:
                ret = dis.get_instructions(clsdict[key])
            # если не функция:
            except TypeError:
                pass
            # если функция:
            else:
                # получаем используемые методы и атрибуты:
                for i in ret:
                    if i.opname == 'LOAD_ATTR' and i.argval not in attributes:
                        attributes.append(i.argval)
                    elif i.opname == 'LOAD_GLOBAL' and i.argval not in methods:
                        methods.append(i.argval)

        # Проверка отсутствия метода 'connect':
        if 'connect' in methods:
            cls.logger.error('Ошибочный метод для "connect" сервера.')
            raise TypeError('Для сервера не используется метод "connect".')

        # Проверка запуска по протоколу TCP:
        if not ('SOCK_STREAM' in attributes and 'AF_INET' in attributes):
            cls.logger.error('Отсутствуют константы "AF_INET" и "SOCK_STREAM" для протокола TCP.')
            raise TypeError('Для работы по TCP необходимо использование "AF_INET" и "SOCK_STREAM".')
        super().__init__(clsname, bases, clsdict)
