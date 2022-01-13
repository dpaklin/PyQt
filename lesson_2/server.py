"""Сервер"""

import select
# import logging
from logs.configs import config_log_server
import argparse
import socket
import sys
from common.utils import *
from common.variables import *
from decorators import Log
from metaclasses import ServerVerifier
from descriptors import Port

SERVER_LOGGER = logging.getLogger('server')


# Класс Сервер:
class Server(metaclass=ServerVerifier):
    listened_port = Port()

    def __init__(self, listened_address, listened_port):
        self.address = listened_address
        self.port = listened_port
        self.sock = None
        # Список клиентов:
        self.clients = []
        # Список отправляемых сообщений:
        self.messages = []
        # Словарь имя-сокет:
        self.names = dict()
        self.logger = logging.getLogger('server')
        super().__init__()

    def create_socket(self):
        """Создает сервер."""
        self.logger.info(
            f'Запущен сервер по адресу: {self.address} на порту: {self.port}.'
        )
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((self.address, self.port))
        server_sock.settimeout(0.2)

        self.sock = server_sock
        self.sock.listen()

    def main_loop(self):
        """Запускает основной цикл сервера."""
        # Инициализируем сокет сервера:
        self.create_socket()
        # Запускаем цикл:
        while True:
            # Ждем подключения, пока не вышел таймаут:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                self.logger.info(f'Установлено соединение с {client_address}.')
                self.clients.append(client)

            recv_list = []
            send_list = []
            err_list = []
            # Проверяем наличие ждущих клиентов:
            try:
                if self.clients:
                    recv_list, send_list, err_list = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass
            # Принимаем сообщения от ждущих клиентов:
            if recv_list:
                for client_with_message in recv_list:
                    try:
                        self.manage_message(get_message(client_with_message), client_with_message)
                    except Exception:
                        self.logger.info(f'Клиент {client_with_message.getpeername()} отключился.')
                        self.clients.remove(client_with_message)
            # Обрабатываем сообщения:
            for message in self.messages:
                try:
                    self.process_message(message, send_list)
                except Exception:
                    self.logger.info(f'Связь с клиентом {message[DESTINATION]} потеряна.')
                    self.remove_client(message[DESTINATION])
            self.messages.clear()

    def check_client_presence(self, message, client):
        """Обрабатывает сообщение о присутствии клиента PRESENCE."""
        # Если не зарегистрирован:
        if message[USER][ACCOUNT_NAME] not in self.names.keys():
            self.names[message[USER][ACCOUNT_NAME]] = client
            response = {RESPONSE: 200}
            send_message(client, response)
        else:
            response = {
                RESPONSE: 400,
                ERROR: 'Имя уже занято.'
            }
            send_message(client, response)
            self.clients.remove(client)
            self.logger.debug(f'Отказ в регистрации клиента {client}.')
            client.close()

    @Log(SERVER_LOGGER)
    def remove_client(self, client_name):
        """Удаляет клиента из списка клиентов."""
        self.clients.remove(self.names[client_name])
        self.names[client_name].close()
        self.logger.debug(f'Клиент {client_name} удален из списка.')
        del self.names[client_name]

    def manage_message(self, message, client):
        """Обрабатывае входящие сообщения по параметру ACTION."""
        self.logger.debug(f'Разбор сообщения от клиента {client}: {message}.')
        # Проверяем регистрацию клиента:
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            self.check_client_presence(message, client)
            return
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.remove_client(ACCOUNT_NAME)
            return
        else:
            response = {
                RESPONSE: 400,
                ERROR: 'Некорректный запрос.'
            }
            send_message(client, response)
            return

    def process_message(self, message, client_list):
        """Отправляет сообщения из списка получателям."""
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in client_list:
            send_message(self.names[message[DESTINATION]], message)
            self.logger.info(f'Отправлено сообщение клиенту {message[DESTINATION]} от клиента {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in client_list:
            self.logger.error(f'Клиент {message[DESTINATION]} не зарегистрирован. Отправка невозможна.')
            raise ConnectionError


@Log(SERVER_LOGGER)
def args_parser():
    """Парсер командной сроки"""
    parser = argparse.ArgumentParser(description='Аргументы командной строки')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, help='Номер порта')
    parser.add_argument('-a', default='', help='Адрес сервера')
    namespace = parser.parse_args(sys.argv[1:])
    listened_address = namespace.a
    listened_port = namespace.p
    return listened_address, listened_port


def main():
    """Создает экземпляр сервера и запускает основной цикл."""
    listened_address, listened_port = args_parser()
    server = Server(listened_address, listened_port)
    server.main_loop()


if __name__ == '__main__':
    main()
