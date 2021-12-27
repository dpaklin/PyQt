"""Тесты сервера"""

import unittest

import sys
import os
PATH = os.path.join(os.getcwd(), '..')
sys.path.append(PATH)
from lesson_2.server import check_client_presence, check_client_message
from lesson_2.common.variables import ACTION, TIME, PROBE, USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR


class ServerTests(unittest.TestCase):
    """Тесты для модуля server.py"""
    error_dict = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    ok_dict = {RESPONSE: 200}

    def setUp(self):
        """Set up for test"""
        print(f'Set up for {self.shortDescription()}')

    def tearDown(self):
        """Tear down for test"""
        print(f'Tear down for {self.shortDescription()}')
        print()

    def test_check_client_message_ok(self):
        """Тест корректного запроса"""
        self.assertEqual(check_client_message({ACTION: '', TIME: 1.123, USER: {ACCOUNT_NAME: 'GUEST'}}),
                         self.ok_dict)

    def test_check_client_message_no_action(self):
        """Тест, когда отсутствует действие"""
        self.assertEqual(check_client_message({TIME: 1.123, USER: {ACCOUNT_NAME: 'GUEST'}}), self.error_dict)

    def test_check_client_message_no_time(self):
        """Тест отсутствия времени в запросе"""
        self.assertEqual(check_client_message({ACTION: '', USER: {ACCOUNT_NAME: 'GUEST'}}), self.error_dict)

    def test_check_client_message_no_user(self):
        """Тест отсутствия пользователя"""
        self.assertEqual(check_client_message({ACTION: '', TIME: 1.123}), self.error_dict)

    def test_check_client_message_unexpected_user(self):
        """Тест некорректного пользователя"""
        self.assertEqual(check_client_message({ACTION: '', TIME: 1.123, USER: {ACCOUNT_NAME: 'WRONG_USER'}}),
                         self.error_dict)

    def test_check_client_presence_ok(self):
        """Тест корректного запроса при проверке на присутствие"""
        self.assertEqual(check_client_presence({ACTION: PRESENCE, TIME: 1.123, USER: {ACCOUNT_NAME: 'GUEST'}}),
                         self.ok_dict)

    def test_check_client_presence_wrong_action(self):
        """Тест неверного действия при проверке присутствия"""
        self.assertEqual(check_client_presence({ACTION: PROBE, TIME: 1.123, USER: {ACCOUNT_NAME: 'GUEST'}}),
                         self.error_dict)


if __name__ == '__main__':
    unittest.main()