from aiogram import Router
from aiogram import F as mF
from aiogram.types import Message, FSInputFile, LinkPreviewOptions
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext

from colorama import Fore as F, Style as S
from datetime import datetime

from scripts import firewall3, tracker, j2, lpsql, memory, parser, messenger
from data import config as cfg, txt

import source.MAIN._keyboards as main_keyboard
from source.MAIN._states import *


rtr = Router()
config = [j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["config_v"]]
firewall3 = firewall3.FireWall('MAIN', silent=False)
db = lpsql.DataBase("lypay_database.db", lpsql.Tables.MAIN)
print("MAIN/abstract router")


@rtr.message(CommandStart(deep_link=False))
async def launch(message: Message, state: FSMContext):
    try:
        memory.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            tracker.log(
                command=("START", F.GREEN + S.BRIGHT),
                from_user=parser.get_user_data(message)
            )
            await message.answer(txt.MAIN.CMD.START, reply_markup=main_keyboard.startCMD)

            if message.from_user.id not in db.searchall("users", "ID"):
                m_id = (await message.answer(
                    txt.MAIN.REGISTRATION.NEW,
                    reply_markup=main_keyboard.registerCMD,
                    link_preview_options=LinkPreviewOptions(is_disabled=True)
                )).message_id
                await (memory.rewrite_sublist(mode='add', name='ccc/main', key=message.chat.id, data=m_id))
                await memory.rewrite_sublist(mode='add', name='hi_frog', key=message.from_user.id,
                                        data=datetime.now().strftime('%Y'))
                await state.set_state(RegisterFSM.STATE0)
            else:
                read_sublist = await memory.read_sublist("hi_frog")
                uid = str(message.from_user.id)
                date = datetime.now().strftime('%Y')
                if read_sublist is None or uid not in read_sublist.keys() or read_sublist[uid] != date:
                    await message.answer_sticker(cfg.MEDIA.FROG_HELLO)
                    await message.answer(txt.MAIN.REGISTRATION.HI_FROG.format(
                        name=' '.join(db.search("users", "ID", message.from_user.id)["name"].split()[:-1])
                    ))
                    await memory.rewrite_sublist(mode='add', name='hi_frog', key=message.from_user.id, data=date)
                await message.answer(txt.MAIN.REGISTRATION.EXISTS,
                                     reply_markup=main_keyboard.update_keyboard(message.from_user.id))
        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(parser.get_user_data(message))
            await message.answer(txt.MAIN.CMD.IN_BLACKLIST)
        else:
            tracker.gray(parser.get_user_data(message))
            await message.answer(txt.MAIN.CMD.NOT_IN_WHITELIST)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(mF.text.in_(("↩️ Отмена", "/cancel")))
async def cancel(message: Message, state: FSMContext):
    try:
        memory.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            current = await state.get_state()
            tracker.log(
                command=("CANCELLED", F.RED + S.BRIGHT),
                from_user=parser.get_user_data(message)
            )
            c = None
            if current in RegisterFSM.__states__:
                await message.answer(txt.MAIN.REGISTRATION.CANCEL,
                                     reply_markup=main_keyboard.update_keyboard(message.from_user.id))
            elif current in TransferFSM.__states__:
                await message.answer(txt.MAIN.TRANSFER.CANCEL,
                                     reply_markup=main_keyboard.update_keyboard(message.from_user.id))
            else:
                c = 0
            for key, value in (await memory.read_sublist("ccc/main")).items():
                if key == str(message.chat.id):
                    await message.bot.edit_message_text(
                        text="[CCC] Действие отменено.",
                        chat_id=key,
                        message_id=int(value)
                    )
                    await message.answer("Последнее действие было сброшено.", reply_markup=main_keyboard.update_keyboard(message.chat.id))
                    await memory.rewrite_sublist(mode='remove', name='ccc/main', key=key, data=value)
                    if c is not None:
                        c += 1
            if c is not None and c == 0:
                await message.answer("Действие отменено.",
                                     reply_markup=main_keyboard.update_keyboard(message.from_user.id))
            await state.clear()
        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(parser.get_user_data(message))
            await message.answer(txt.MAIN.CMD.IN_BLACKLIST)
        else:
            tracker.gray(parser.get_user_data(message))
            await message.answer(txt.MAIN.CMD.NOT_IN_WHITELIST)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(mF.text == "💳 Пополнить баланс")
async def deposit(message: Message):
    try:
        memory.update_config(config, [txt, cfg, main_keyboard])
        if (await j2.fromfile_async(cfg.PATHS.LAUNCH_SETTINGS))["main_can_deposit"]:
            if message.from_user.id in db.searchall("users", "ID"):
                firewall_status = firewall3.check(message.from_user.id)
                if firewall_status == firewall3.WHITE_ANCHOR:
                    tracker.log(
                        command=("DEPOSIT", F.CYAN + S.BRIGHT),
                        status=("SUCCESS", F.GREEN + S.BRIGHT),
                        from_user=parser.get_user_data(message)
                    )
                    qr = db.search("qr", "userID", message.from_user.id)
                    if qr is None or qr["fileID_main"] is None:
                        fileid = (await message.answer_photo(FSInputFile(cfg.PATHS.QR + str(message.from_user.id) + '.png'),
                                                             txt.MAIN.DEPOSIT.MAIN, has_spoiler=True)).photo[-1].file_id
                        db.update("qr", "userID", message.from_user.id, "fileID_main", fileid)
                    else:
                        await message.answer_photo(qr["fileID_main"], txt.MAIN.DEPOSIT.MAIN, has_spoiler=True)
                elif firewall_status == firewall3.BLACK_ANCHOR:
                    tracker.black(parser.get_user_data(message))
                    await message.answer(txt.MAIN.CMD.IN_BLACKLIST)
                else:
                    tracker.gray(parser.get_user_data(message))
                    await message.answer(txt.MAIN.CMD.NOT_IN_WHITELIST)
            else:
                tracker.log(
                    command=("DEPOSIT", F.CYAN + S.BRIGHT),
                    status=("NOT_REGISTERED", F.RED),
                    from_user=parser.get_user_data(message)
                )
                await message.answer(txt.MAIN.REGISTRATION.NOT_REGISTERED)
        else:
            tracker.log(
                command=("DEPOSIT", F.CYAN + S.BRIGHT),
                status=("SETTINGS_ACTION_FORBIDDEN", F.RED),
                from_user=parser.get_user_data(message)
            )
            await message.answer(txt.MAIN.DEPOSIT.FORBIDDEN_BY_SETTINGS)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(mF.text.in_(("💰 Баланс", "😱 Баланс")))
async def balance(message: Message):
    try:
        memory.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            try:
                balance_ = db.balance_view(message.from_user.id)
                await message.answer(f"Ваш баланс: {balance_ if balance_ else 0} {cfg.VALUTA.SHORT}")
                tracker.log(
                    command=("BALANCE", F.MAGENTA + S.DIM),
                    from_user=parser.get_user_data(message)
                )
            except lpsql.errors.IDNotFound:
                await message.answer(txt.MAIN.REGISTRATION.NOT_REGISTERED)
                tracker.log(
                    command=("BALANCE", F.MAGENTA + S.DIM),
                    status=("NOT_REGISTERED", F.RED + S.DIM),
                    from_user=parser.get_user_data(message)
                )
        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(parser.get_user_data(message))
            await message.answer(txt.MAIN.CMD.IN_BLACKLIST)
        else:
            tracker.gray(parser.get_user_data(message))
            await message.answer(txt.MAIN.CMD.NOT_IN_WHITELIST)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(mF.text == "⚙️ Авторы")
async def credits_(message: Message):
    try:
        memory.update_config(config, [txt, cfg, main_keyboard])
        await message.answer_photo(cfg.MEDIA.CREDITS, caption=txt.MAIN.CREDITS.TEXT)
        tracker.log(
            command=("CREDITS", F.LIGHTMAGENTA_EX + S.DIM),
            from_user=parser.get_user_data(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("get_qr"))
async def get_qr(message: Message):
    try:
        memory.update_config(config, [txt, cfg, main_keyboard])
        firewall_status = firewall3.check(message.from_user.id)
        if firewall_status == firewall3.WHITE_ANCHOR:
            user = db.search("users", "ID", message.from_user.id)
            if user is not None:
                await message.answer(txt.MAIN.CMD.QR_WARNING.format(
                    name=user["name"],
                    tag='@'+user["tag"] if user["tag"] else '–'
                ))
                qr = db.search("qr", "userID", message.from_user.id)
                if qr is None or qr["fileID_main"] is None:
                    fileid = (await message.answer_photo(FSInputFile(cfg.PATHS.QR + str(message.from_user.id) + '.png'),
                                                         has_spoiler=True)).photo[-1].file_id
                    db.update("qr", "userID", message.from_user.id, "fileID_main", fileid)
                else:
                    await message.answer_photo(qr["fileID_main"], has_spoiler=True)
                tracker.log(
                    command=("GET_QR", F.BLACK + S.BRIGHT),
                    from_user=parser.get_user_data(message)
                )
            else:
                tracker.log(
                    command=("GET_QR", F.BLACK + S.BRIGHT),
                    status=("NOT_REGISTERED", F.RED),
                    from_user=parser.get_user_data(message)
                )
                await message.answer(txt.MAIN.REGISTRATION.NOT_REGISTERED)
        elif firewall_status == firewall3.BLACK_ANCHOR:
            tracker.black(parser.get_user_data(message))
            await message.answer(txt.MAIN.CMD.IN_BLACKLIST)
        else:
            tracker.gray(parser.get_user_data(message))
            await message.answer(txt.MAIN.CMD.NOT_IN_WHITELIST)
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


# @rtr.message(Command("delete"))
async def delete_acc(message: Message):
    try:
        try:
            db.delete_user(message.from_user.id)
            await message.answer("Account deleted.")
        except lpsql.errors.IDNotFound:
            await message.answer("Account doesn't exist.")
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )


@rtr.message(Command("help"))
async def help_(message: Message):
    try:
        memory.update_config(config, [txt, cfg, main_keyboard])
        await message.answer_document(cfg.MEDIA.MANUAL.MAIN, caption=txt.MAIN.CMD.MANUAL)
        tracker.log(
            command=("HELP", F.LIGHTBLUE_EX),
            from_user=parser.get_user_data(message)
        )
    except Exception as e:
        tracker.error(
            e=e,
            userID=message.from_user.id
        )
