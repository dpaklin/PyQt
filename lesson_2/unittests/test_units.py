"""Тесты утилит"""

import unittest
import json

import sys
import os
PATH = os.path.join(os.getcwd(), '..')
sys.path.append(PATH)
from common.utils import get_message, send_message
from common.variables import ACTION, TIME, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR, ENCODING


class TestSocket():
    """Тестовый сокет"""
    def __init__(self, dict_test):
        self.dict_test = dict_test
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        """Кодирует отправляемое сообщение"""
        json_test_message = json.dumps(self.dict_test)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def recv(self, max_len):
        """Получает данные из сокета"""
        json_test_message = json.dumps(self.dict_test)
        return json_test_message.encode(ENCODING)


class GetMessageTests(unittest.TestCase):
    """Тесты для модуля units.py"""
    dict_received_ok = {RESPONSE: 200}
    dict_received_error = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    dict_test = {
        ACTION: PRESENCE,
        TIME: 1.123,
        USER: {
            ACCOUNT_NAME: 'TEST'
        }
    }

    def test_get_message_ok(self):
        """Тест корректного приема сообщений"""
        test_socket_ok = TestSocket(self.dict_received_ok)
        self.assertEqual(get_message(test_socket_ok), self.dict_received_ok)

    def test_get_message_error(self):
        """Тест некорректной расшифровки"""
        test_socket_error = TestSocket(self.dict_received_error)
        self.assertEqual(get_message(test_socket_error), self.dict_received_error)

    def test_send_message_ok(self):
        """Тест корректной отправки сообщений"""
        # тестовый сокет
        test_socket = TestSocket(self.dict_test)
        # тестируемая функция передает в тестовый сокет
        send_message(test_socket, self.dict_test)
        # сравнение кодировок
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)
        # проверка исключения
        with self.assertRaises(Exception):
            send_message(test_socket, test_socket)


if __name__ == '__main__':
    unittest.main()