from os import execle, environ
from sys import executable

from pyrogram import Client
from pyrogram.types import Message

from ahmedyad.Keyboards import login_key
from ahmedyad.Redis import db
from ahmedyad.get_session import getSession
from ahmedyad.yad import Bfilter


@Client.on_message(Bfilter("⌯ تسجيل الدخول"))
async def login_to_me(client: Client, message: Message):
    user, get_me, session = await getSession(message, login_key)
    db.set(f'{client.me.id}:{get_me.id}:session', session)
    db.set(f'{client.me.id}:restart', '3yad')
    await message.reply('⌯ تم تسجيل الدخول انتظر 5 ثواني')
    args = [executable, "main.py"]
    execle(executable, *args, environ)
