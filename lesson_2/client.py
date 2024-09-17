"""Клиент"""

import logging
import logs.configs.config_log_client
import argparse
import sys
import socket
import threading
import time
import json
from common.variables import *
from common.utils import get_message, send_message
from decorators import Log
from metaclasses import ClientVerifier

CLIENT_LOGGER = logging.getLogger('client')


# Класс Клиент:
class Client(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.sock = sock
        self.account_name = account_name
        self.logger = logging.getLogger('client')
        super().__init__()

    @staticmethod
    def display_help():
        """Выводит информацию о командах."""
        print('Поддерживаемые команды:')
        print('msg - отправить сообщение.')
        print('help - вывести подсказки по командам.')
        print('exit - выход из программы.')

    def create_exit_message(self):
        """Формирует сообщение о выходе."""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def create_message(self):
        """Формирует сообщение и отправляет его на сервер."""
        destination = input('Кому: ')
        message_text = input('Сообщение: ')
        message_dict = {
            ACTION: MESSAGE,
            TIME: time.time(),
            SENDER: self.account_name,
            DESTINATION: destination,
            MESSAGE_TEXT: message_text
        }
        self.logger.debug(f'Сформировано сообщение: {message_dict}.')
        try:
            send_message(self.sock, message_dict)
            self.logger.info(f'Отправлено сообщение для клиента {destination}.')
        except Exception:
            self.logger.critical('Потеряно соединение с сервером.')
            sys.exit(1)


# Класс Клиент, отправляющий сообщения:
class ClientSender(Client):
    def run(self):
        """Основной цикл отправки сообщений."""
        self.display_help()
        while True:
            command = input('Введите команду: ')
            if command == 'msg':
                self.create_message()
            elif command == 'help':
                self.display_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except Exception:
                    pass
                print('Завершение сеанса.')
                self.logger.info(f'Клиент {self.account_name} завершил сеанс.')
                time.sleep(0.5)
                break
            else:
                print('Неизвестная команда. Попробуйте "help".')


# Класс Клиент, принимающий сообщения:
class ClientReceiver(Client):
    def run(self):
        """Основной цикл приема сообщений."""
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and message[DESTINATION] == self.account_name and MESSAGE_TEXT in message:
                    print()
                    print(f'От {message[SENDER]}:\n'
                          f'{message[MESSAGE_TEXT]}')
                    self.logger.info(f'Клиентом {message[DESTINATION]} от клиента {message[SENDER]} '
                                     f'получено сообщение: {message[MESSAGE_TEXT]}')
                else:
                    self.logger.error(f'Получено некорректное сообщение: {message}.')
            except (OSError, ConnectionError, ConnectionResetError, ConnectionAbortedError):
                self.logger.critical('Потеряно соединение с сервером.')
            except json.JSONDecodeError:
                self.logger.critical('Не удалось декодировать сообщение.')
                break


@Log(CLIENT_LOGGER)
def args_parser():
    """Парсер командной сроки"""
    parser = argparse.ArgumentParser(description='Аргументы командной строки')
    parser.add_argument('-a', default=DEFAULT_IP_ADDRESS, help='Адрес сервера')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, help='Номер порта')
    parser.add_argument('-n', '--name', default=None, help='Имя клиента')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.a
    server_port = namespace.p
    account_name = namespace.name

    if not 1024 <= server_port <= 65535:
        CLIENT_LOGGER.critical(f'Значение порта должно лежать в диапазоне 1024 - 65535.\n'
                               f'Значение {server_port} вне допустимого диапазона!')
        sys.exit(1)
    return server_address, server_port, account_name


@Log(CLIENT_LOGGER)
def create_presence(account_name):
    """Формирует сообщение о присутствии клиента."""
    out_msg = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
        }
    }
    CLIENT_LOGGER.debug(f'Создано сообщение о присутствии клиента {account_name}.')
    return out_msg


@Log(CLIENT_LOGGER)
def analyze_response_answer(message):
    """Анализирует ответ сервера."""
    CLIENT_LOGGER.debug(f'Анализ сообщения от сервера\n'
                        f'{message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 - Ok'
        return f'400 - {message[ERROR]}'
    return ValueError


def main():
    """
    Запуск командной строки.
    Первый параметр - адрес сервера.
    Второй параметр - порт.
    Третий - имя.
    """
    print('Клиентский модуль.')
    server_address, server_port, account_name = args_parser()
    if not account_name:
        account_name = input('Введите имя пользователя: ')
    print(f'Пользователь {account_name}.')

    CLIENT_LOGGER.info(f'Запуск клиента.\n'
                       f'   Адрес сервера - {server_address}.'
                       f'   Порт для подключения - {server_port}.'
                       f'   Имя пользователя - {account_name}')

    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((server_address, server_port))
        message_for_presence = create_presence(account_name)
        send_message(client_sock, message_for_presence)
        answer_of_server = analyze_response_answer(get_message(client_sock))
        CLIENT_LOGGER.info(f'Получен ответ от сервера {answer_of_server}')
        print('Соединение установлено.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error(f'Невозможно декодировать сообщение, полученное от сервера.')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(f'Отказ в соединении со стороны сервера! '
                               f'Сервер {server_address}:{server_port}')
        sys.exit(1)
    else:
        sender = ClientSender(account_name, client_sock)
        sender.daemon = True
        sender.start()

        receiver = ClientReceiver(account_name, client_sock)
        receiver.daemon = True
        receiver.start()

        while True:
            time.sleep(1)
            if receiver.is_alive() and sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()