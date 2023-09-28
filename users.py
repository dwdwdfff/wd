import os
import re
from asyncio import sleep, create_task, get_event_loop
from sys import argv
import logging
import random
from pyrogram import Client, filters, idle
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait, YouBlockedUser
from telebot.async_telebot import AsyncTeleBot
from PIL import Image
import io
from ahmedyad.Redis import db
from info import token, sudo_id, user_bot

bot = AsyncTeleBot(token)


userbot = Client(
    f'users/user:{argv[1][:15]}',
    26720165,
    '79eca4750dca2f63156c0c2b59d4af7d',
    session_string=argv[1]
)

logging.getLogger("pyrogram").setLevel(logging.CRITICAL)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
async def getInfo():
    return await bot.get_me(), \
        await bot.get_chat(sudo_id)


async def lf(_, __, msg):  # فلتر الرابط
    if msg.text:
        if '?' in msg.text:
            return False
    return True


bot.me, sudo_info = get_event_loop().run_until_complete(getInfo())

userbot.send_log = lambda text: \
    bot.send_message(sudo_info.id, f"⌯ اشعار من الحساب : {userbot.me.id}\n{text}")

getvp = lambda bot_id, owner_id: 1000 \
    if not db.get(f'{bot_id}:{owner_id}:points') else int(db.get(f'{bot_id}:{owner_id}:points'))

async def auto_delete_link():
    while not await sleep(600):
        for msg in db.smembers(f'{bot.me.id}:{userbot.me.id}:click'):
            msg = msg.split(':')
            await userbot.request_callback_answer(
                chat_id=msg[0],
                message_id=msg[1],
                callback_data=msg[2]
            )


async def delete_userbot():
    while not await sleep(5):
        if db.sismember(f'{bot.me.id}:{sudo_info.id}:delete_userbot', userbot.me.id):
            db.srem(f'{bot.me.id}:{sudo_info.id}:delete_userbot', userbot.me.id)
            db.srem(f'{bot.me.id}:{sudo_info.id}:sessions', userbot.session_string)
            await userbot.stop()
            try:
                os.remove(userbot.name)
            except:
                pass
            await userbot.send_log('⌯ تم حذف الحساب')
            exit()


async def auto_start_in_bot():
    while not await sleep(300):
        if not db.get(f'{bot.me.id}:{userbot.me.id}:stop'):
            try:
                await userbot.send_message(user_bot, '/start')
            except YouBlockedUser:
                await userbot.unblock_user(user_bot)
                await sleep(1)
                await userbot.send_message(user_bot, '/start')
            except Exception as e:
                print(e)
                pass


async def join_chat(c, link, bot_id):
    try:
        if '+' in link or 'joinchat' in link:
            await c.join_chat(link)
        else:
            await c.join_chat(link.replace('https://t.me/', ''))
    except FloodWait as e:
        await c.send_log(f'⌯ انحظر لمدة {e.value} ثانيه')
        if e.value >= 99999:
            db.set(f'{bot.me.id}:{c.me.id}:get_all_points', '3yad')
            await c.send_message(bot_id, '/start')
        db.setex(f'{bot.me.id}:{userbot.me.id}:stop', e.value + 10, '3yad')
        await sleep(e.value + 10)
        await c.send_log('⌯ الحظر اتفك')
    except Exception as e:
        print(e)


@userbot.on_message(filters.bot & filters.regex('بوت تمويل العرب') & filters.private)
async def start_in_bot(c, msg):  # الشاشه الرئيسيه في البوت
    points = int(msg.reply_markup.inline_keyboard[0][0].text.split(': ')[1])
    if points >= 100:
        if (points >= getvp(bot.me.id, sudo_info.id) or
            db.get(f'{bot.me.id}:{c.me.id}:get_all_points')) and \
                not db.get(f'{bot.me.id}:{c.me.id}:whit_for_time'):
            await c.send_log(f'⌯ جاري تحويل {points - 25} نقطه اليك')
            try:
                await c.request_callback_answer(
                    chat_id=msg.chat.id,
                    message_id=msg.id,
                    callback_data='sendtocount'
                )
            except:
                pass
            await sleep(1)
            await msg.reply(points - 25)
            return
    if not db.get(f'{bot.me.id}:{userbot.me.id}:stop'):
        try:
            await c.request_callback_answer(
                chat_id=msg.chat.id,
                message_id=msg.id,
                callback_data='col'
            )
        except:
            pass
        await sleep(1)
        try:
            await c.request_callback_answer(
                chat_id=msg.chat.id,
                message_id=msg.id,
                callback_data='col3'
            )
        except:
            pass


@userbot.on_edited_message(filters.bot & filters.regex('اشترك في ') & filters.private)
async def join_chats(c, msg):  # تجميع نقاط الاشتراك
    if not db.get(f'{bot.me.id}:{userbot.me.id}:stop'):
        await sleep(1)
        await join_chat(c, msg.reply_markup.inline_keyboard[0][0].url, msg.chat.id)
        await sleep(1)
        try:
            await c.request_callback_answer(
                chat_id=msg.chat.id,
                message_id=msg.id,
                callback_data=msg.reply_markup.inline_keyboard[1][0].callback_data
            )
        except:
            pass


@userbot.on_message(filters.bot & filters.regex("بواسطه رابط التحويل الخاص بك") & filters.private)
async def block_and_leave_all(c, msg):
    await c.block_user(msg.chat.id)
    db.setex(f'{bot.me.id}:{c.me.id}:stop', 99999999999999999999999999, '3yad')
    async for dialog in c.get_dialogs():
        if dialog.chat.type != ChatType.PRIVATE:
            try:
                await c.leave_chat(dialog.chat.id, delete=True)
            except:
                pass


@userbot.on_message(filters.bot & filters.regex('https://t.me/(.*)?start=(.*)') & filters.private)
async def cpab(c, msg):  # نقل النقاط
    ay = ''
    for lin in msg.text.split('\n'):
        if 't.me' in lin:
            ay = lin
            break
    if not ay:
        return
    link = 'http' + ay.split('http')[1]
    db.delete(f'{bot.me.id}:{c.me.id}:get_all_points')
    url = link.replace('https://t.me/', '').split('?start=')
    db.sadd(f'{bot.me.id}:{sudo_info.id}:links', url[1])
    db.sadd(f'{bot.me.id}:{c.me.id}:click',
            f'{msg.chat.id}:{msg.id}:{msg.reply_markup.inline_keyboard[0][0].callback_data}')

@userbot.on_message(filters.bot & filters.regex('تم حظرك لمده دقيقه بسبب التكرار') & filters.private)
async def stop1m(c, msg):
    db.setex(f'{bot.me.id}:{c.me.id}:stop', 60, '3yad')


@userbot.on_message(filters.bot & filters.regex('يجب ان نتحقق من انك لست روبوت') & filters.private)
async def send_contact(c, msg):  # ارسال جها الاتصال للتحقق
    get_me = await c.get_me()
    await c.send_contact(
        msg.chat.id,
        get_me.phone_number,
        first_name=get_me.first_name,
        last_name=get_me.last_name,
        reply_to_message_id=msg.id
    )


@userbot.on_message(filters.bot & filters.regex('https://t.me/') & filters.create(lf) & filters.private)
async def ctcbot(c, msg):  # الاشتراك الاجباري
    if not db.get(f'{bot.me.id}:{userbot.me.id}:stop'):
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
        await join_chat(c, link, msg.chat.id)
        await sleep(1)
        await c.send_message(msg.chat.id, '/start')


@userbot.on_message(filters.bot & filters.regex('t.me/') & filters.create(lf) & filters.private)
async def ctccccbot(c, msg):  # الاشتراك الاجباري
    if not db.get(f'{bot.me.id}:{userbot.me.id}:stop'):
        ay = ''
        for lin in msg.text.split('\n'):
            if 't.me' in lin:
                ay = lin
                break
        if not ay:
            return
        link = 't.me' + ay.split('t.me')[1]
        if ' ' in link:
            link = link.split(' ')[0]
        await join_chat(c, link, msg.chat.id)
        await sleep(1)
        await c.send_message(msg.chat.id, '/start')


def get_random_username():
    with open('username.txt', 'r') as file:
        usernames = file.readlines()
    username = random.choice(usernames).strip()
    # إضافة حرف ورقم عشوائيين إلى اليوزرنيم
    random_char = random.choice('abcdefghijklmnopqrstuvwxyz')
    random_digit = random.choice('0123456789')
    username += random_char + random_digit + random_char
    return username

def get_random_first_name():
    with open('name.txt', 'r') as file:
        first_names = file.readlines()
    return random.choice(first_names).strip()

def get_random_bio():
    with open('bio.txt', 'r') as file:
        bios = file.readlines()
    return random.choice(bios).strip()


async def main():
    await userbot.start()
    await userbot.update_profile(first_name=get_random_first_name())
    await userbot.update_profile(bio=get_random_bio())
    await userbot.enable_cloud_password("0", hint="mody0")
    await userbot.set_username(get_random_username())

    photo_path = f'photo/{random.choice(os.listdir("photo"))}'
    if os.path.isfile(photo_path):
                with open(photo_path, 'rb') as photo_file:
                    photo_data = photo_file.read()
                    await userbot.set_profile_photo(photo=io.BytesIO(photo_data))
    async for dialog in userbot.get_dialogs():
         if dialog.chat.type != ChatType.PRIVATE:
            try:
                await userbot.leave_chat(dialog.chat.id, delete=True)
                await userbot.delete_messages(dialog.chat.id, delete=True)
            except:
                pass
    try:
        await userbot.send_log('⌯ تم تشغيل الحساب')
    except Exception as e:
        print(e)
    await idle()
    await userbot.stop()


get_event_loop().run_until_complete(main())
