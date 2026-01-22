from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import FSInputFile, ReactionTypeEmoji

from asyncio import sleep

from data.txt import EXE
from data.config import WARNING_GROUP
from scripts.parser import parse_media_cache_ad_packet
from source.references import MAIN, LPSB, LPAA


async def message(*, bot: str, chatID: int, text: str,
                  file: str | None = None, file_mode: str | None = None,
                  update_keyboard: ... = lambda t: None) -> None:
    """
    Отправляет сообщение с указанными параметрами

    :param bot: 'MAIN' | 'LPSB' | 'LPAA'
    :param chatID: chatID получателя (userID)
    :param text: текст
    :param file: путь к фото или файлу для отправки (опц.)
    :param file_mode: режим отправки (опц., нужно указать file): 'file' отправит как файл,
    'photo_upload' загрузит файл как фото с диска, 'photo_cache' запросит кэшированное фото с серверов ТГ,
    'video_upload' и 'video_cache' сделают то же самое для видео,
    'media_cache_ad' отправит медиа группу, собранную по ID объектов в file_path (ad only)
    'set_reaction' поставит реакцию на сообщение для chat_id=participantID, message_id=file_path
    'sticker' отправит стикер по ID из file_mode
    :param update_keyboard: функция обновления reply-клавиатуры (опц.), если указана, то автоматически применится,
    параметр `to` передастся в качестве аргумента
    """
    if len(text) == 0 or file_mode not in ('file', 'photo_upload', 'photo_cache', 'video_upload', 'video_cache',
                                           'media_cache_ad', 'set_reaction', 'sticker', None):
        raise ValueError("Аргументы функции scripts.messaging.message указанны неверно.")

    bot = bot.upper()
    if bot == 'MAIN':
        bot_ref = MAIN
    elif bot == 'LPSB':
        bot_ref = LPSB
    elif bot == 'LPAA':
        bot_ref = LPAA
    else:
        raise ValueError("Параметр 'bot' функции scripts.messaging.message указан неверно.")

    ok = False
    tries = -2

    while not ok:
        tries += 1
        try:
            if file_mode is None:
                await bot_ref.send_message(chatID, text, reply_markup=update_keyboard(chatID))
            elif file_mode == 'photo_upload':
                await bot_ref.send_photo(chatID, FSInputFile(file), caption=text, reply_markup=update_keyboard(chatID))
            elif file_mode == 'photo_cache':
                await bot_ref.send_photo(chatID, file, caption=text, reply_markup=update_keyboard(chatID))
            elif file_mode == 'video_upload':
                await bot_ref.send_video(chatID, FSInputFile(file), caption=text, reply_markup=update_keyboard(chatID))
            elif file_mode == 'video_cache':
                await bot_ref.send_video(chatID, file, caption=text, reply_markup=update_keyboard(chatID))
            elif file_mode == 'media_cache_ad':
                data = list()
                for line in file.split(''):
                    data.append(line.split(':', 2))
                packet = text.split('\u00a0')
                await parse_media_cache_ad_packet(tech_message=packet[0], sender_id=packet[1], group_id=chatID,
                                                  data=data)
            elif file_mode == 'set_reaction':  # to_ - chat_id; text - reaction; file_ - message_id
                await bot_ref.set_message_reaction(
                    chat_id=chatID,
                    message_id=int(file),
                    reaction=[ReactionTypeEmoji(emoji=text[0])]
                )
            elif file_mode == 'sticker':
                await bot_ref.send_sticker(chatID, file, reply_markup=update_keyboard(chatID))
            else:  # file_mode == 'file'
                await bot_ref.send_document(chatID, FSInputFile(file), caption=message, reply_markup=update_keyboard(chatID))
            ok = True
        except TelegramRetryAfter:
            await sleep(2.71828180 ** tries / 2)
        except Exception as e:
            print(chatID, e, e.args)
            await warn(text=EXE.ALERTS.MESSAGE_SEND_FAIL.format(
                bot=bot_ref.token,
                id=chatID
            ))
            return


async def warn(*, text: str):
    """
    Отправляет оповещение в группу варнингов (config.WARNING_GROUP)

    :param text: текст предупреждения
    """
    await message(bot='LPAA', chatID=WARNING_GROUP, text=text)


async def error_traceback(*, error_text: str, error_log: str):
    """
    Отправляет ошибку (+ лог) в группу варнингов (config.WARNING_GROUP)

    :param error_text: текст ошибки
    :param error_log: путь до файла с логом
    """
    await message(bot='LPAA', chatID=WARNING_GROUP, text=error_text, file=error_log, file_mode='file')
