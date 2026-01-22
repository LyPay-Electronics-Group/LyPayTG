from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from asyncio import sleep

from scripts import j2, lpsql, parser, tracker
from data import config as cfg, txt
from source.references import LPSB

db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)


async def cheque(*, storeID: str, chequeID: str):
    """
    Отправляет чек заданному магазину

    :param storeID: ID магазина
    :param chequeID: ID чека для отправки
    """
    try:
        if (await j2.fromfile_async(cfg.PATHS.LAUNCH_SETTINGS))["auction"]:
            keyboard_markup = None
        else:
            keyboard_ = InlineKeyboardBuilder()
            keyboard_.add(
                InlineKeyboardButton(text="Возврат денежных средств", callback_data=f"cheque_cancel_{chequeID}_cb"))
            keyboard_markup = keyboard_.as_markup()

        cheque_ = await j2.fromfile_async(cfg.PATHS.STORES_CHEQUES + f"{chequeID}.json")
        user_ = db.search("users", "ID", cheque_["customer"])

        generated_strings = list()
        items_ = cheque_["items"]
        multipliers_ = cheque_["multipliers"]
        for _ in range(len(items_)):
            text = parser.de_anchor(items_[_]["text"])
            multy = multipliers_[_]
            price = items_[_]["price"]
            generated_strings.append(f"{text} × {multy} | {price * multy} {cfg.VALUTA.SHORT}")

        for shopkeeper in map(lambda d: d["userID"], db.search("shopkeepers", "storeID", storeID, True)):
            await LPSB.send_message(shopkeeper, txt.LPSB.CHEQUE.TABLET.format(
                cheque_id=chequeID,
                name=user_["name"],
                group=user_["class"],
                tag='@' + user_["tag"] if user_["tag"] else '–',
                items=txt.MAIN.STORE.CHEQUE_GENERATED_STRINGS_SEPARATOR.join(generated_strings),
                total=cheque_["price"]
            ), reply_markup=keyboard_markup)
            await sleep(1 / 30)
    except Exception as e:
        tracker.error(
            e=e,
            userID=0
        )
