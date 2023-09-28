from asyncio import sleep

from pyrogram import Client, filters
import logging
logging.getLogger("pyrogram").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)


async def lf(_, __, msg):  # فلتر الرابط
    if msg.text:
        if '?' in msg.text:
            return False
        return True
    return False


@Client.on_message(filters.bot & filters.regex('https://t.me/') & filters.create(lf) & filters.private)
async def ctcbot(c, msg):  # الاشتراك الاجباري
    ay = ''
    for lin in msg.text.split('\n'):
        if 't.me' in lin:
            ay = lin
            break
    if not ay:
        return
    link = 'http' + ay.split('http')[1]
    if ' ' in link:
        link = link.split(' ')[0]
    if '+' in link or 'joinchat' in link:
        await c.join_chat(link)
    else:
        await c.join_chat(link.replace('https://t.me/', ''))
    await sleep(1)
    await c.send_message(msg.chat.id, '/start')
