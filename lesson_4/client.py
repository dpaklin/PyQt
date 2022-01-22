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
from client_db import ClientStorage

CLIENT_LOGGER = logging.getLogger('client')

# Класс Клиент:
class Client(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.sock = sock
        self.account_name = account_name
        self.logger = logging.getLogger('client')
        self.database = database
        super().__init__()


# Класс Клиент, отправляющий сообщения:
class ClientSender(Client):
    @staticmethod
    def display_help():
        """Выводит информацию о командах."""
        print('Поддерживаемые команды:')
        print('msg - отправить сообщение.')
        print('contacts - получить список контактов.')
        print('add - добавить контакт.')
        print('del - удалить контакт.')
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
        # Сохраняем сообщение в базе:
        self.database.save_message(self.account_name, destination, message_text)
        # Отправка сообщения на сервер:
        try:
            send_message(self.sock, message_dict)
            self.logger.info(f'Отправлено сообщение для клиента {destination}.')
        except Exception:
            self.logger.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    def run(self):
        """Основной цикл отправки сообщений."""
        self.display_help()
        while True:
            command = input('Введите команду: ')
            # Запрос на отправку сообщения:
            if command == 'msg':
                self.create_message()
            # Запрос подсказки:
            elif command == 'help':
                self.display_help()
            # Запрос на выход:
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except Exception:
                    pass
                print('Завершение сеанса.')
                self.logger.info(f'Клиент {self.account_name} завершил сеанс.')
                time.sleep(0.2)
                break
            # Запрос списка контактов:
            elif command == 'contacts':
                contacts = self.database.get_contacts()
                for contact in contacts:
                    print(contact)
            # Запрос на добавление контакта:
            elif command == 'add':
                contact_name = input('Введите имя контакта: ')
                self.database.add_contact(contact_name)
                self.logger.debug('Контакт добавлен в клиентскую базу.')
                try:
                    add_contact(self.sock, self.account_name, contact_name)
                except Exception:
                    self.logger.error(f'Контакт {contact_name} не добавлен.')
            # Запрос на удаление контакта:
            elif command == 'del':
                contact_name = input('Введите имя контакта: ')

                self.database.remove_contact(contact_name)
                try:
                    remove_contact(self.sock, self.account_name, contact_name)
                except Exception:
                    self.logger.error(f'Контакт {contact_name} не удален.')
            else:
                print('Неизвестная команда. Попробуйте "help".')


# Класс Клиент, принимающий сообщения:
class ClientReceiver(Client):
    def run(self):
        """Основной цикл приема сообщений."""
        while True:
            try:
                message = get_message(self.sock)
            except (OSError, ConnectionError, ConnectionResetError, ConnectionAbortedError):
                self.logger.critical('Потеряно соединение с сервером.')
                break
            except json.JSONDecodeError:
                self.logger.critical('Не удалось декодировать сообщение.')
                break
            else:
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and message[DESTINATION] == self.account_name and MESSAGE_TEXT in message:
                    print()
                    print(f'От {message[SENDER]}:\n'
                          f'{message[MESSAGE_TEXT]}')
                    self.logger.info(f'Клиентом {message[DESTINATION]} от клиента {message[SENDER]} '
                                     f'получено сообщение: {message[MESSAGE_TEXT]}')
                    # Сохраняем сообщение в базе:
                    self.database.save_message(message[SENDER], self.account_name, message[MESSAGE_TEXT])
                elif RESPONSE in message and message[RESPONSE] == 200:
                    print('Операция добавления/удаления клиента выполнена!')
                else:
                    self.logger.error(f'Получено некорректное сообщение: {message}.')


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
def create_presence(account_name: str):
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


def get_contacts_list(sock, account_name: str):
    """Возвращает список контактов пользователя."""
    request = {
        ACTION: GET_CONTACTS,
        USER: account_name,
        TIME: time.time()
    }
    send_message(sock, request)
    answer = get_message(sock)
    if RESPONSE in answer and answer[RESPONSE] == 202:
        return answer[CLIENTS_LIST]
    else:
        raise ERROR('Ошибка сервера!')


def connect_db(sock, database, account_name: str):
    """Загружает базу данных клиента."""
    try:
        contacts = get_contacts_list(sock, account_name)
    except Exception:
        CLIENT_LOGGER.error('Ошибка получения контактов!')
    else:
        for contact in contacts:
            database.add_contact(contact)


def add_contact(sock, user_name: str, contact_name: str):
    """Запрос на добавление контакта."""
    CLIENT_LOGGER.debug(f'Добавление контакта {contact_name} в базу сервера.')
    request = {
        ACTION: ADD_CONTACT,
        USER: user_name,
        ACCOUNT_NAME: contact_name,
        TIME: time.time()
    }
    send_message(sock, request)
    answer = get_message(sock)
    if RESPONSE in answer and answer[RESPONSE] == 200:
        pass
    else:
        raise Exception('Контакт не добавлен!')
    print('Контакт добавлен.')


def remove_contact(sock, user_name: str, contact_name: str):
    """Запрос на удаление контакта."""
    CLIENT_LOGGER.debug(f'Удаление контакта {contact_name}')
    request = {
        ACTION: REMOVE_CONTACT,
        USER: user_name,
        ACCOUNT_NAME: contact_name,
        TIME: time.time()
    }
    send_message(sock, request)
    answer = get_message(sock)
    if RESPONSE in answer and answer[RESPONSE] == 200:
        pass
    else:
        raise Exception('Контакт не удален!')
    print('Контакт удален.')


def main(db_path='test'):
    """
    Запуск командной строки.
    Первый параметр - адрес сервера.
    Второй параметр - порт.
    Третий - имя.
    """
    print('[Client started...]')
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
        # База данных:
        database = ClientStorage(db_path, account_name)
        connect_db(client_sock, database, account_name)

        sender = ClientSender(account_name, client_sock, database)
        sender.daemon = True
        sender.start()

        receiver = ClientReceiver(account_name, client_sock, database)
        receiver.daemon = True
        receiver.start()

        while True:
            time.sleep(1)
            if receiver.is_alive() and sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
