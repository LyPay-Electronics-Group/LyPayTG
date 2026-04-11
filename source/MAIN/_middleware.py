from typing import Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from scripts import tracker, parser


class MessageLogging(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, ...]], Awaitable[...]],
        event: Message,
        data: Dict[str, ...]
    ):
        """
        Вызов middleware для пакетов с сообщениями (Message update)
        """
        tracker.log(
            command=("middleware call", ''),
            from_user=parser.get_user_data(event)
        )
        print(handler.__name__)
        return await handler(event, data)
