from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F as mF

from colorama import Fore as F, Style as S

from scripts import j2, tracker, lpsql, memory, parser, messenger
from data import config as cfg, txt


rtr = Router()
config = [j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("LPSB/cheques router")


@rtr.callback_query(mF.data.find("cheque_cancel_") != -1)
async def cancel_cheque(callback: CallbackQuery):
    try:
        memory.update_config(config, [txt, cfg])
        await callback.answer()
        tracker.log(
            command=("CHEQUE", F.LIGHTGREEN_EX + S.BRIGHT),
            status=("RETURN", F.LIGHTGREEN_EX + S.BRIGHT),
            from_user=parser.get_user_data(callback)
        )
        cheque_id = callback.data.replace("cheque_cancel_", '').replace("_cb", '')
        keyboard = InlineKeyboardBuilder([[
            InlineKeyboardButton(text=f"🟩 Да, вернуть {cfg.VALUTA.NAME[6]}", callback_data=f"cheque_return_{cheque_id}_cb"),
            InlineKeyboardButton(text="🟥 Нет, отменить возврат", callback_data="cheque_deny_cb")
        ]])
        keyboard.adjust(1)
        await callback.message.answer(f"Вы уверены, что хотите вернуть чек #cheque_{cheque_id}?", reply_markup=keyboard.as_markup())
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data == "cheque_deny_cb")
async def cancel_cancelling_cheque(callback: CallbackQuery):
    try:
        memory.update_config(config, [txt, cfg])
        await callback.message.edit_text(txt.LPSB.CHEQUE.CHEQUE_RETURN_CANCELLED)
        await callback.answer()
        tracker.log(
            command=("CHEQUE", F.LIGHTGREEN_EX + S.BRIGHT),
            status=("CANCELLED_RETURN", F.GREEN + S.DIM),
            from_user=parser.get_user_data(callback)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )


@rtr.callback_query(mF.data.find("cheque_return_") != -1)
async def confirm_cancelling_cheque(callback: CallbackQuery):
    try:
        memory.update_config(config, [txt, cfg])
        cheque_id = callback.data.replace("cheque_return_", '').replace("_cb", '')
        cheque = await j2.fromfile_async(cfg.PATHS.STORES_CHEQUES + f"{cheque_id}.json")
        if cheque["status"]:
            cheque["status"] = False
            with open(cfg.PATHS.STORES_CHEQUES + f"{cheque_id}.json", 'w', encoding='utf8') as file:
                file.write(j2.to_(cheque))

            db.transfer(cheque_id.split('_')[1], cheque["customer"], cheque["price"])

            await callback.message.edit_text(txt.LPSB.CHEQUE.RETURN.format(amount=cheque["price"]))
            await messenger.message(
                text=txt.LPSB.CHEQUE.RETURN_CUSTOMER.format(id=cheque_id),
                bot="MAIN",
                chatID=cheque["customer"]
            )
            tracker.log(
                command=("CHEQUE", F.LIGHTGREEN_EX + S.BRIGHT),
                status=("RETURNED", F.LIGHTYELLOW_EX + S.BRIGHT),
                from_user=parser.get_user_data(callback)
            )
        else:
            await callback.message.edit_text(txt.LPSB.CHEQUE.INACTIVE_CHEQUE)
            tracker.log(
                command=("CHEQUE", F.LIGHTGREEN_EX + S.BRIGHT),
                status=("FAILED_RETURN", F.LIGHTRED_EX + S.DIM),
                from_user=parser.get_user_data(callback)
            )
        await callback.answer()
    except Exception as e:
        tracker.error(
            e=e,
            userID=callback.from_user.id
        )
