from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from os import getenv
from dotenv import load_dotenv
from sys import argv

from asyncio import run, sleep
from colorama import Fore as F, Style as S, init as col_init, just_fix_windows_console

from scripts import j2, tracker
import scripts.memory
from data import config as cfg

from source.SRV.manual_media_id_2 import rtr as manual_media_id_r


col_init(autoreset=True)
just_fix_windows_console()
load_dotenv()

storage = MemoryStorage()
disp = Dispatcher(storage=storage)
auc = j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)["auction"]
if auc:
    from source.AUC.abstract import rtr as abstract_r
    from source.LPSB.access import rtr as access_r
    from source.AUC.transfer import rtr as transfer_r
    disp.include_routers(
        abstract_r,
        access_r,
        transfer_r,
        manual_media_id_r
    )
else:
    from source.LPSB.abstract import rtr as abstract_r
    from source.LPSB.access import rtr as access_r
    from source.LPSB.cheques import rtr as cheques_r
    from source.LPSB.registration import rtr as registration_r
    from source.LPSB.menu import rtr as menu_r
    from source.LPSB.ad import rtr as ad_r  # !
    from source.LPSB.ad_admins import rtr as ad_admins_r  # !
    disp.include_routers(
        ad_admins_r,  # !
        abstract_r,
        ad_r,
        access_r,
        cheques_r,
        registration_r,
        menu_r,
        manual_media_id_r
    )
bot = Bot(getenv("LYPAY_STORES_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@disp.startup()
async def ccc_on_startup():
    for key, value in (await scripts.memory.read_sublist("ccc/lpsb")).items():
        try:
            await bot.edit_message_text(
                text="Сервер был перезапущен, сообщение с клавиатурой удалено автоматически. Последнее действие было сброшено.",
                chat_id=key,
                message_id=int(value)
            )
            await sleep(0.015)
            await scripts.memory.rewrite_sublist(
                mode='remove',
                name='ccc/lpsb',
                key=key
            )
        except Exception as e:
            tracker.error(
                e=e,
                userID=0
            )


# -=-=-=-

async def main():
    settings = j2.fromfile(cfg.PATHS.LAUNCH_SETTINGS)
    if settings["launch"] and argv[1] == settings["launch_stamp"]:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            del_web = F.LIGHTBLACK_EX + S.BRIGHT + "- skipping webhooks... " + S.RESET_ALL + F.LIGHTGREEN_EX + "[OK]"
        except:
            del_web = F.LIGHTBLACK_EX + S.BRIGHT + "- skipping webhooks... " + S.RESET_ALL + F.RED + "[FAILED]"

        set_name = [F.LIGHTBLACK_EX + S.BRIGHT + "- set name..."]
        if settings["update_names"]:
            for name in cfg.NAMES.AUC if auc else cfg.NAMES.LPSB:
                try:
                    await bot.set_my_name(name=name[0], language_code=name[1])
                    set_name.append(F.LIGHTBLACK_EX + S.BRIGHT + f"   > {name[1] if name[1] else 'null'} : "
                                    + S.RESET_ALL + F.LIGHTGREEN_EX + "[OK]")
                except:
                    set_name.append(F.LIGHTBLACK_EX + S.BRIGHT + f"   > {name[1] if name[1] else 'null'} : "
                                    + S.RESET_ALL + F.RED + "[FAILED]")
        else:
            set_name[0] += S.RESET_ALL + F.YELLOW + " [SKIPPED]"

        try:
            await bot.set_my_commands([
                BotCommand(command=cmd[0], description=cmd[1])
                for cmd in (cfg.COMMANDS.AUC if auc else cfg.COMMANDS.LPSB)
            ])
            set_cmd = F.LIGHTBLACK_EX + S.BRIGHT + "- set commands... " + S.RESET_ALL + F.LIGHTGREEN_EX + "[OK]"
        except:
            set_cmd = F.LIGHTBLACK_EX + S.BRIGHT + "- set commands... " + S.RESET_ALL + F.RED + "[FAILED]"

        started = "\nSTARTED!"

        tracker.startup("auc" if auc else "lpsb", del_web, *set_name, set_cmd, started)

        await disp.start_polling(bot)
    else:
        print("Bad start; you have to use official Launcher!")


if __name__ == "__main__":
    run(main())
