""" Конфигурация logger'а для клиента """

import logging
from logging import handlers
import os
import sys


# Определяем путь для логов:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_TO_LOG_DIR = '../log_client/'
PATH = os.path.join(BASE_DIR, PATH_TO_LOG_DIR, 'client.log')

# Создааем logger:
LOGGER = logging.getLogger('client')

# Настраиваем форматирование логов:
FORMATTER = logging.Formatter('%(asctime)-23s || %(levelname)-8s || %(name)-6s <==> %(message)s')

# Создаем обработчик для вывода в поток ошибок:
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

# Создаем обработчик для вывода в файл:
FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(PATH, when='d', interval=1, encoding='utf8')
FILE_HANDLER.setFormatter(FORMATTER)

# Настраиваем logger:
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(logging.DEBUG)


if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка!!!')
    LOGGER.error('Ошибка!!')
    LOGGER.warning('Предупреждение!')
    LOGGER.info('Информационное сообщение.')
    LOGGER.debug('Отладочная информация.')
