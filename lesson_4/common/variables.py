"""Константы"""

# Порт по умолчанию:
DEFAULT_PORT = 7777
# Адрес по умолчанию для подключения клиента:
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений:
MAX_CONNECTIONS = 5
# Максимальная длмна сообщений:
MAX_PACKAGE_LENGTH = 1024
# Кодировка:
ENCODING = 'utf-8'

# Основные ключи JIM-протокола
ACTION = 'action'
TIME = 'time'
TYPE = 'type'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# Прочие ключи протокола:
PRESENCE = 'presence'
PROBE = 'probe'
MSG = 'msg'
QUIT = 'quit'
AUTHENTICATE = 'authenticate'
JOIN = 'join'
LEAVE = 'leave'
STATUS = 'status'
RESPONSE = 'response'
ALERT = 'alert'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
ADD_CONTACT = 'add_contact'
REMOVE_CONTACT = 'remove_contact'
CLIENTS_LIST = 'clients_list'
EDIT_CONTACT = 'edit_contact'