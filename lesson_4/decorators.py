"""Декораторы"""

import traceback
import inspect


class Log:
    """Класс-декоратор"""

    def __init__(self, logger):
        """Назначение соответствующего loggera"""
        self.logger = logger

    def __call__(self, func_to_log):
        def log_saver(*args, **kwargs):
            """Обертка"""
            res = func_to_log(*args, **kwargs)
            self.logger.debug(f'Была вызвана функция {func_to_log.__name__} c параметрами {args}, {kwargs}. '
                              f'Вызов из модуля {func_to_log.__module__}. Вызов из'
                              f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
                              f'Вызов из функции {inspect.stack()[1][3]}')
            return res

        return log_saver