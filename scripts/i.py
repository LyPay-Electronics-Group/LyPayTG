symbols = list('0123456789abcdefghijklmnopqrstuvwxyz')


def to_id(__num__: int, __length__: int = 2) -> str:
    """
    :param __num__: Число в 10-ричной системе счисления для перевода в 36-ричную
    :param __length__: Количество символов (отсчитывая с конца строки)
    :return: Число в 36-ричной системе счисления
    """
    __ans__ = ''
    while __num__ > 0:
        __ans__ = symbols[__num__ % 36] + __ans__
        __num__ //= 36
    return __ans__[:__length__].zfill(__length__)


def to_int(__id__: str) -> int:
    """
    :param __id__: Число в 36-ричной системе счисления для перевода в 10-ричную
    :return: Число в 10-ричной системе счисления
    """
    return int(__id__, base=36)
