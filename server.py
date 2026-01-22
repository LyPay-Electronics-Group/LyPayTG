from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from os import getenv
from dotenv import load_dotenv


load_dotenv()

storage = MemoryStorage()
disp = Dispatcher(storage=storage)
bot = Bot(getenv("LYPAY_SUB_SERVER_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
