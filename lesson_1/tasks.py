from ipaddress import ip_address
from subprocess import Popen, PIPE
from tabulate import tabulate


def host_ping(list_ip_addresses, timeout=500, requests=1):
    """
    1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
    Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
    В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего
    сообщения («Узел доступен», «Узел недоступен»).
    При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
    :param list_ip_addresses: ip-адресс или имя хоста (строка)
    :param timeout: время ожидания ответа
    :param requests: количество запросов к адресату
    :return: список адресов
    """
    results = {'Доступные узлы': "", 'Недоступные узлы': ""}  # словарь с результатами
    for address in list_ip_addresses:
        try:
            address = ip_address(address)
        except ValueError:
            pass
        proc = Popen(f"ping {address} -w {timeout} -n {requests}", shell=False, stdout=PIPE)
        proc.wait()
        # проверяем код завершения подпроцесса
        if proc.returncode == 0:
            results['Доступные узлы'] += f"{str(address)}\n"
            res_string = f'{address} - Узел доступен'
        else:
            results['Недоступные узлы'] += f"{str(address)}\n"
            res_string = f'{address} - Узел недоступен'
        print(res_string)
    return results


def host_range_ping():
    """
    2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
    Меняться должен только последний октет каждого адреса. По результатам проверки должно выводиться
    соответствующее сообщение.
    :return: список перебранных адресов
    """
    while True:
        # запрос первоначального адреса
        start_ip = input('Введите первоначальный адрес: ')
        try:
            # смотрим чему равен последний октет
            las_oct = int(start_ip.split('.')[3])
            break
        except Exception as e:
            print(e)
    while True:
        # запрос на количество проверяемых адресов
        end_ip = input('Сколько адресов проверить?: ')
        if not end_ip.isnumeric():
            print('Необходимо ввести число: ')
        else:
            # по условию меняется только последний октет
            if (las_oct + int(end_ip)) > 254:
                print(f"Можем менять только последний октет, т.е. "
                      f"максимальное число хостов для проверки: {254 - las_oct}")
            else:
                break

    host_list = []
    # формируем список ip адресов
    [host_list.append(str(ip_address(start_ip) + x)) for x in range(int(end_ip))]
    # передаем список в функцию из задания 1 для проверки доступности
    return host_ping(host_list)


def host_range_ping_tab():
    """
    3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
    Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате
    (использовать модуль tabulate). Таблица должна состоять из двух колонок и выглядеть примерно так:
    Reachable
    10.0.0.1
    10.0.0.2
    Unreachable
    10.0.0.3
    :return: none
    """
    # запрашиваем хосты, проверяем доступность, получаем словарь результатов
    res_dict = host_range_ping()
    print()
    # выводим в табличном виде
    print(tabulate([res_dict], headers='keys', tablefmt="pipe", stralign="center"))


if __name__ == '__main__':
    ip_addresses = ['ya.ru', 'gb.ru', '192.168.1.1', '192.168.0.1']

    host_ping(ip_addresses)
    print('=' * 50)
    host_range_ping_tab()