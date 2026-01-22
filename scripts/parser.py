from aiogram.types import Message as aio_message, CallbackQuery as aio_callback, InputMediaPhoto, InputMediaVideo

from data.config import QUOTATION_ANCHOR, NEW_LINE_ANCHOR, OPEN_CURLY_BRACKET_ANCHOR, CLOSE_CURLY_BRACKET_ANCHOR, SPACE_ANCHOR
from source.references import LPSB
from scripts.memory import rewrite_sublist


async def parse_media_cache_ad_packet(*, tech_message: str, sender_id: int | str, group_id: int, data: list[list[str]]):
    """
    Обрабатывает запрос отправки рекламы (в группу модерации) (для LPSB)

    :param tech_message: блок с техническим текстом
    :param sender_id: userID отправителя для записи в саблист
    :param group_id: ID группы модерации
    :param data: распакованные медиа в формате
    """
    if data[0][0] in ('photo', 'video'):
        m_id = (await LPSB.send_media_group(group_id, [
            (
                InputMediaPhoto(
                    media=data[i][1],
                    caption=data[i][2] if len(data[i]) > 2 and data[i][2] != "None" else None
                )
                if data[i][0] == 'photo' else
                InputMediaVideo(
                    media=data[i][1],
                    caption=data[i][2] if len(data[i]) > 2 and data[i][2] != "None" else None
                )
            ) for i in range(len(data))
        ]))[0].message_id
    else:
        m_id = (await LPSB.send_message(group_id, data[0][2])).message_id
    m_id_2 = (await LPSB.send_message(group_id, tech_message, reply_to_message_id=m_id)).message_id
    await rewrite_sublist(name='ad_approving', key=str(m_id_2), data=str(sender_id))


def anchor(__s__: str) -> str:
    """
    :param __s__: строка для якорного преобразования
    :return: строка с якорями
    """
    return __s__.replace(
        '\n', NEW_LINE_ANCHOR
    ).replace(
        '{', OPEN_CURLY_BRACKET_ANCHOR
    ).replace(
        '}', CLOSE_CURLY_BRACKET_ANCHOR
    ).replace(
        '"', QUOTATION_ANCHOR
    ).replace(
        ' ', SPACE_ANCHOR
    )


def de_anchor(__s__: str) -> str:
    """
    :param __s__: строка для обратного якорного преобразования
    :return: строка без якорей
    """
    return __s__.replace(
        NEW_LINE_ANCHOR, '\n'
    ).replace(
        OPEN_CURLY_BRACKET_ANCHOR, '{'
    ).replace(
        CLOSE_CURLY_BRACKET_ANCHOR, '}'
    ).replace(
        QUOTATION_ANCHOR, '"'
    ).replace(
        SPACE_ANCHOR, ' '
    )


def get_user_data(__object__: aio_message | aio_callback) -> tuple[int, str | None]:
    """
    Парсит telegram id и telegram username из объекта сообщения или коллбека

    :param __object__: aiogram message или callback
    :return: (obj.from_user.id, obj.from_user.username)
    """
    return __object__.from_user.id, __object__.from_user.username
