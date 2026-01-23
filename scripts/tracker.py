from asyncio import create_task as aio_create_task

from datetime import datetime
from colorama import Fore, Style, init as c_init
from pyfiglet import figlet_format as media_text
from html import escape

from traceback import format_exc
from os import environ, getcwd
from platform import system
from sys import version_info as version

from scripts import lpsql, messenger
from scripts.unix import unix
from data.config import PATHS, NAME, VERSION
from data.txt import LPAA as t_LPAA, EXE as t_EXE

c_init(autoreset=True)

db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)

platform = system()
if platform == "Windows":
    py_bin = environ['LOCALAPPDATA'] + fr"\Programs\Python\Python{version.major}{version.minor}\Lib"
elif platform == "Linux":
    py_bin = getcwd() + f"/.venv/lib/python{version.major}.{version.minor}"
else:
    py_bin = '%%%'

BOT = ''
LENGTH = 36


def startup(bot: str, *updates: str) -> None:
    """
    Печатает в консоль приветствие

    :param bot: main | lpaa | lpsb | auc
    """
    bot = bot.upper()
    if bot not in ("MAIN", "LPAA", "LPSB", "AUC"):
        raise ValueError
    global BOT
    BOT = bot

    bot_text = media_text("LyPay | " + bot)
    version_text = media_text(' '.join(list(VERSION)))
    print(bot_text)
    print(version_text)
    print(NAME)
    print("INFO LOGS", datetime.now().strftime('%d/%m/%y'))
    print()
    for u in updates:
        print(u)
    print()


def log(*, command: tuple[str, str], status: tuple[str, str] = None, from_user: tuple[int, str | None]) -> None:
    """
    Простой лог

    :param command: первая часть, текст / цвет
    :param status: вторая часть, текст / цвет
    :param from_user: (userID, tag)
    """
    t = datetime.now()
    print()
    length = LENGTH - len(command[0])

    if check(from_user):
        update(from_user)

    if status is None:
        print(
            '[', ' ' * (length % 2 + length // 2), command[1] + command[0],
            ' ' * (length // 2), ']',
            sep='', end='   '
        )
    else:
        length -= len(status[0]) + 1
        print(
            '[', ' ' * (length % 2 + length // 2),
            command[1] + command[0], ':',
            status[1] + status[0],
            ' ' * (length // 2), ']',
            sep='', end='   '
        )
    print(
        '[',
        Fore.YELLOW + Style.DIM + t.strftime('%X'),
        ']',
        end='   '
    )
    print(
        '[',
        Fore.CYAN + Style.BRIGHT + str(from_user[1] if from_user[1] else from_user[0]),
        ']',
        end='   '
    )
    if BOT == "LPSB" or BOT == "AUC":
        store = db.search("shopkeepers", "userID", from_user[0])
        if store:
            print(
                '[',
                Fore.GREEN + Style.BRIGHT + store["storeID"] + Style.RESET_ALL,
                ']',
                end=''
            )
    print()


def black(from_user: tuple[int, str | None]) -> None:
    log(
        command=("IN_BLACKLIST", Fore.RED + Style.BRIGHT),
        from_user=from_user
    )
    aio_create_task(
        messenger.warn(text=t_EXE.WHITELIST.BLACK.format(id=from_user[0], tag='@' + from_user[1] if from_user[1] else '–'))
    )


def gray(from_user: tuple[int, str | None]) -> None:
    log(
        command=("NOT_IN_WHITELIST", Fore.RED + Style.BRIGHT),
        from_user=from_user
    )
    aio_create_task(
        messenger.warn(text=t_EXE.WHITELIST.GRAY.format(id=from_user[0], tag='@' + from_user[1] if from_user[1] else '–')),
    )


def censor(*, from_user: tuple[int, str | None], text: str, text_length_flag: bool = True) -> str | None:
    """
    Возвращает текст, в котором безопасно заменены html-последовательности, если сообщение прошло проверку. None -- в обратном случае.

    :param from_user: (telegram id, telegram tag)
    :param text: текст для проверки и замены
    :param text_length_flag: флаг проверки длины текста. True -- если проверка длины необходима
    :return: str | None
    """
    list_gray = ["https", "http"]
    list_black = []
    gray_warn = False
    black_warn = False

    if text_length_flag and len(text) >= 250:
        gray_warn = True
    if not gray_warn:
        for line in list_gray:
            if text.find(line) != -1:
                gray_warn = True
                break

    for line in list_black:
        if text.find(line) != -1:
            black_warn = True
            break

    if black_warn:
        aio_create_task(
            messenger.warn(text=t_LPAA.SPAM_B.format(
                user=from_user[0],
                bot=BOT,
                message=text.replace('<', '‹').replace('>', '›')
            ))
        )
        return None
    if gray_warn:
        aio_create_task(
            messenger.warn(text=t_LPAA.SPAM.format(
                user=from_user[0],
                bot=BOT,
                message=text
            ))
        )

    return escape(text)


def check(from_user: tuple[int, str | None]) -> bool | None:
    user = db.search("users", "ID", from_user[0])
    if user is None:
        return None
    return user["tag"] != from_user[1]


def update(from_user: tuple[int, str | None]) -> None:
    db.update("users", "ID", from_user[0], "tag", from_user[1])


def error(*, e: Exception, userID: int) -> None:
    unix_timestamp = unix()
    error_timestamp = f"error_{round(unix_timestamp * 100)}"
    full_trace = format_exc()
    log_path = PATHS.EXE + f"{error_timestamp}.log"

    with open(log_path, 'w', encoding='utf8') as tmp_f:
        tmp_f.write(full_trace)

    crop_trace = full_trace[full_trace.rfind("File \""):]

    crop_trace = crop_trace.strip()
    aio_create_task(
        messenger.error_traceback(
            error_text=f"#{error_timestamp}\n\nlast trace call:\n<code>{escape(crop_trace)}</code>\n\nuser id: <code>{userID}</code>",
            error_log=log_path
        )
    )

    file_ = 5
    trace = crop_trace[file_+1:]
    file_str = trace[:trace.find(',')-1]

    line_ = len(file_str) + 8
    trace = trace[line_:]
    line_str = trace[:trace.find(',')]

    in_ = len(line_str) + 5
    trace = trace[in_:]
    in_str = trace[:trace.find('\n')]

    print()
    print("Error ", Fore.RED + f"#{error_timestamp}", ':', sep='')
    print(Fore.BLUE + "TIME:", Fore.LIGHTBLACK_EX + datetime.fromtimestamp(unix_timestamp).strftime('%X'))
    print(Fore.GREEN + "NAME:", Fore.LIGHTBLACK_EX + get_full_class_error_name(e))
    print(Fore.YELLOW + "FILE:", Fore.LIGHTBLACK_EX + file_str.replace(py_bin, '%pyBIN%'))
    print(Fore.YELLOW + "LINE:", Fore.LIGHTBLACK_EX + line_str)
    print(Fore.YELLOW + "IN:  ", Fore.LIGHTBLACK_EX + in_str)
    print()


def get_full_class_error_name(obj: Exception):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__
