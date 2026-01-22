from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv
from os import getenv

load_dotenv()


MAIN = Bot(getenv("LYPAY_MAIN_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
LPSB = Bot(getenv("LYPAY_STORES_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
LPAA = Bot(getenv("LYPAY_ADMINS_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
