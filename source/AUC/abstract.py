from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S
from random import randint

from scripts import firewall3, tracker, lpsql, memory, parser
from scripts.j2 import fromfile as j_fromfile
from data import txt, config as cfg


rtr = Router()
firewall3 = firewall3.FireWall('LPSB', silent=False)
config = [j_fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("AUC/abstract router")


@rtr.message(Command("start"))
async def start(message: Message):
    try:
        memory.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            await message.answer(txt.AUC.CMD.START)
            tracker.log(
                command=("START", F.GREEN + S.BRIGHT),
                from_user=parser.get_user_data(message)
            )
        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(parser.get_user_data(message))
            await message.answer(txt.AUC.CMD.IN_BLACKLIST)
        else:
            tracker.gray(parser.get_user_data(message))
            await message.answer(txt.AUC.CMD.NOT_IN_WHITELIST)
            await message.answer_sticker(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS[
                                             randint(0, len(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS)-1)
                                         ])
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    try:
        memory.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            tracker.log(
                command=("CANCELLED", F.RED + S.BRIGHT),
                from_user=parser.get_user_data(message)
            )
            c = 0
            for key, value in (await memory.read_sublist('ccc/lpsb')).items():
                if key == str(message.chat.id):
                    c += 1
                    await message.bot.edit_message_text(
                        text="[CCC] Действие отменено.",
                        chat_id=key,
                        message_id=value
                    )
                    await memory.rewrite_sublist(
                        mode='remove',
                        name='ccc/lpsb',
                        key=key
                    )
            if c == 0:
                await message.answer(txt.LPSB.CMD.CANCELLED)
            await state.clear()

            try:
                storeID = db.search("shopkeepers", "userID", message.from_user.id)
                if storeID is None:
                    return
                storeID = storeID["storeID"]
                while True:
                    db.delete("changing", message.from_user.id, storeID)
            except lpsql.errors.EntryNotFound:
                pass
        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(parser.get_user_data(message))
            await message.answer(txt.AUC.CMD.IN_BLACKLIST)
        else:
            tracker.gray(parser.get_user_data(message))
            await message.answer(txt.AUC.CMD.NOT_IN_WHITELIST)
            await message.answer_sticker(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS[
                                             randint(0, len(cfg.MEDIA.NOT_IN_LPSB_WHITELIST_FROGS)-1)
                                         ])
            tracker.log(
                command=("NOT_IN_WHITELIST", F.RED + S.BRIGHT),
                from_user=parser.get_user_data(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("balance"))
async def balance(message: Message):
    try:
        memory.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            balance_ = db.balance_view(db.search("shopkeepers", "userID", message.from_user.id)["storeID"])
            await message.answer(f"Ваш баланс: {balance_ if balance_ else 0} {cfg.VALUTA.SHORT}")
            tracker.log(
                command=("BALANCE", F.MAGENTA + S.DIM),
                from_user=parser.get_user_data(message)
            )
        elif firewall_status == firewall3.BLACK_ANCHOR:
            await message.answer(txt.AUC.CMD.IN_BLACKLIST)
            tracker.log(
                command=("IN_BLACKLIST", F.RED + S.BRIGHT),
                from_user=parser.get_user_data(message)
            )
        else:
            await message.answer(txt.AUC.CMD.NOT_IN_WHITELIST)
            tracker.log(
                command=("NOT_IN_WHITELIST", F.RED + S.BRIGHT),
                from_user=parser.get_user_data(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("auc"))
async def get_auc_num(message: Message):
    try:
        memory.update_config(config, [txt, cfg])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            await message.answer(txt.AUC.CMD.AUC_NUM.format(num=db.search(
                "stores",
                "ID",
                db.search("shopkeepers", "userID", message.from_user.id)["storeID"])["auctionID"]
            ))
            tracker.log(
                command=("AUCTION_NUMBER", F.GREEN + S.DIM),
                from_user=parser.get_user_data(message)
            )
        elif firewall_status == firewall3.BLACK_ANCHOR:
            await message.answer(txt.AUC.CMD.IN_BLACKLIST)
            tracker.log(
                command=("IN_BLACKLIST", F.RED + S.BRIGHT),
                from_user=parser.get_user_data(message)
            )
        else:
            await message.answer(txt.AUC.CMD.NOT_IN_WHITELIST)
            tracker.log(
                command=("NOT_IN_WHITELIST", F.RED + S.BRIGHT),
                from_user=parser.get_user_data(message)
            )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
