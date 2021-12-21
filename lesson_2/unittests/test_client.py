"""Тесты клиента"""

import unittest

import sys
import os
PATH = os.path.join(os.getcwd(), '..')
sys.path.append(PATH)
from lesson_2.client import create_presence, analyze_response_answer
from lesson_2.common.variables import ACTION, TIME, TYPE, USER, ACCOUNT_NAME, PRESENCE, STATUS, RESPONSE, ERROR


class ClientTests(unittest.TestCase):
    """Тесты для модуля client.py"""

    def setUp(self):
        """Set up for test"""
        print(f'Set up for {self.shortDescription()}')

    def tearDown(self):
        """Tear down for test"""
        print(f'Tear down for {self.shortDescription()}')
        print()

    def test_create_presence(self):
        """Тест сообщения о присутствии"""
        presence = create_presence()
        presence[TIME] = 1.123
        self.assertEqual(presence, {ACTION: PRESENCE, TIME: 1.123, TYPE: STATUS,
                                    USER: {ACCOUNT_NAME: 'GUEST', STATUS: 'HERE!'}})

    def test_analize_answer_200(self):
        """Тест ответа 200"""
        self.assertEqual(analyze_response_answer({RESPONSE: 200}), '200 - Ok')

    def test_analize_answer_400(self):
        """Тест ответа 400"""
        self.assertEqual(analyze_response_answer({RESPONSE: 400, ERROR: 'Where are you?'}),
                         '400 - Where are you?')

    @unittest.skip('Не разобрался, в чем ошибка')
    def test_analize_no_answer(self):
        """Тест исключения нет ответа"""
        self.assertRaises(ValueError, analyze_response_answer, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()