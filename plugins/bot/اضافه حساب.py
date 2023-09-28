from pyrogram import Client
from pyrogram.types import Message

from ahmedyad.Keyboards import start_key
from ahmedyad.Redis import db
from ahmedyad.get_session import getSession
from ahmedyad.yad import Bfilter


@Client.on_message(Bfilter("⌯ اضافة حساب"))
async def login_to_other(client: Client, message: Message):
    if db.scard(f'{client.me.id}:{message.from_user.id}:sessions') <= 9999:
        user, get_me, session = await getSession(message, start_key)
        db.sadd(f'{client.me.id}:{message.from_user.id}:sessions', session)
        await message.reply('⌯ تم تسجيل الدخول الي الحساب بنجاح', reply_markup=start_key)
    else:
        await message.reply('⌯ لقد وصلت الي الحد الاقصي من الحسابات')
