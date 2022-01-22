"""Утилиты"""

import json
from lesson_2.common.variables import MAX_PACKAGE_LENGTH, ENCODING
from lesson_2.decorators import Log
import logging
import sys


if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


@Log(LOGGER)
def get_message(sock):
    """Принимает байты и декодирует в словарь"""
    encoded_response = sock.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        response = json.loads(encoded_response.decode(ENCODING))
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


@Log(LOGGER)
def send_message(sock, message):
    """Кодирует словарь и отправляет его"""
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    sock.send(encoded_message)
