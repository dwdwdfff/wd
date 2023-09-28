from pyrogram import Client, filters
import logging
logging.getLogger("pyrogram").setLevel(logging.CRITICAL)


@Client.on_message(filters.bot & filters.regex('يجب ان نتحقق من انك لست روبوت') & filters.private)
async def send_contact(c, msg):
    get_me = await c.get_me()
    await c.send_contact(
        msg.chat.id,
        get_me.phone_number,
        first_name=get_me.first_name,
        last_name=get_me.last_name,
        reply_to_message_id=msg.id
    )


@Client.on_message(filters.bot & filters.regex('تم التحقق') & filters.private)
async def send_start_to_bot(c, m):
    await c.send_message(m.chat.id, '/start')
