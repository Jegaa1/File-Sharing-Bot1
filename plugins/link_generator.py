from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import requests
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

def shorten_url_with_tinyurl(long_url):
    try:
        response = requests.get(f"http://tinyurl.com/api-create.php?url={long_url}")
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to shorten URL: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error shortening URL: {e}")
        return None

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask("Forward the First Message from DB Channel (with Quotes)..\nor Send the DB Channel Post Link", chat_id=message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue

    while True:
        try:
            second_message = await client.ask("Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id=message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    long_link = f"https://tamilserialbot1.jasurun.workers.dev?start={base64_string}"
    short_link = shorten_url_with_tinyurl(long_link)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={short_link}')]])
    await second_message.reply_text(f"<b>8 into 1: {short_link}</b>", quote=True, reply_markup=reply_markup)

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask("Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id=message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote=True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    long_link = f"https://tamilserialbot1.jasurun.workers.dev?start={base64_string}"
    short_link = shorten_url_with_tinyurl(long_link)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={short_link}')]])
    await channel_message.reply_text(f"Link: {short_link}", quote=True, reply_markup=reply_markup)
