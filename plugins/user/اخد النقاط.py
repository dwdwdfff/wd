from asyncio import create_task, sleep

from ahmedyad.Redis import db
from ahmedyad.get_info import sudo_info
from ahmedyad.yad import Bot, sudo_client
from info import user_bot
import logging
logging.getLogger("pyrogram").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

async def collect_points():
    while not await sleep(10):
        for link in db.smembers(f'{Bot.me.id}:{sudo_info.id}:links'):
            db.srem(f'{Bot.me.id}:{sudo_info.id}:links', link)
            await sudo_client.send_message(user_bot, f'/start {link}')
            await sleep(5)


create_task(collect_points())
