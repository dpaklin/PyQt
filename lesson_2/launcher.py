"""Launcher - запускает сервер и два клиентских приложения client1 и client2."""

import subprocess
import sys

PROCESS = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')
    if ACTION == 'q':
        break
    elif ACTION == 's':
        clients_quantity = int(input('Укажите количество запускаемых клиентов: '))
        if sys.platform == 'win32':
            PROCESS.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
            for i in range(clients_quantity):
                PROCESS.append(subprocess.Popen(f'python client.py -n client{i + 1}',
                                                creationflags=subprocess.CREATE_NEW_CONSOLE))
        else:
            PROCESS.append(subprocess.Popen('python server.py'))
            for i in range(clients_quantity):
                PROCESS.append(subprocess.Popen(f'python client.py -n client{i + 1}'))
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
