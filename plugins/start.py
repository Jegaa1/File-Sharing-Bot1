import asyncio
import base64
import logging
import os
import random
import re
import string
import time
from datetime import datetime, time as dt_time, timedelta

from pyrogram import Client, filters, __version__, emoji
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import (
    ADMINS,
    FORCE_MSG,
    START_MSG,
    CUSTOM_CAPTION,
    IS_VERIFY,
    SHORTLINK_API,
    SHORTLINK_URL,
    DISABLE_CHANNEL_BUTTON,
    PROTECT_CONTENT,
    TUT_VID,
    OWNER_ID,
)
from helper_func import subscribed, encode, decode, get_messages, get_shortlink, get_verify_status, update_verify_status, get_exp_time
from database.database import add_user, del_user, full_userbase, present_user
from shortzy import Shortzy

SECONDS = int(os.getenv("SECONDS", "600"))

WAIT_MSG = """<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a reply to any telegram message with out any spaces.</code>"""
ADMINS = [880087645]

def get_time_until_midnight():
    now = datetime.now()
    eleven_fifty_nine_pm = datetime.combine(now.date(), dt_time(23, 59))
    return (eleven_fifty_nine_pm - now).total_seconds()

def get_exp_time(seconds):
    return str(timedelta(seconds=int(seconds)))

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id

    # Check if user is an admin
    if id in ADMINS:
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('〆 மெயின் சேனல் 〆', url='https://t.me/+enbcoW7Zebk2NmY9')],
                [InlineKeyboardButton('🍃 விஜய் டிவி​ 🍃', url='https://t.me/+CJghbYKDPtM0MmJl'), InlineKeyboardButton('🔆 சன் டிவி 🔆', url='https://t.me/+56ze8w46Xj4zYjNl')],
                [InlineKeyboardButton('🎭 ஜி தமிழ் 🎭', url='https://t.me/+VdExpPLNSLVlMTdl'), InlineKeyboardButton('♻️ CWC Tamil ♻️', url='https://t.me/+EPYGIZ6a035jYjBl')]
            ]
        )

        await message.reply("Welcome, owner/admin! You have special privileges.", reply_markup=reply_markup)
        return

    # Add user if not present
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass

    # Check verification status
    verify_status = await get_verify_status(id)
    if verify_status['is_verified'] and (time.time() - verify_status['verified_time']) > get_time_until_midnight():
        await update_verify_status(id, is_verified=False)

    if "verify_" in message.text:
        _, token = message.text.split("_", 1)
        if verify_status['verify_token'] != token:
            return await message.reply("Your token is invalid or expired. Try again by clicking /start")
        
        await update_verify_status(id, is_verified=True, verified_time=time.time())
        await message.reply("Your token is successfully verified and valid until 11:59 PM", protect_content=False, quote=True)
        return

    elif len(message.text) > 7 and verify_status['is_verified']:
        # Add logic to handle messages when user is verified
        pass

    elif verify_status['is_verified']:
        # Send start message if user is verified
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('〆 மெயின் சேனல் 〆', url='https://t.me/+enbcoW7Zebk2NmY9')],
                [InlineKeyboardButton('🍃 விஜய் டிவி​ 🍃', url='https://t.me/+CJghbYKDPtM0MmJl'), InlineKeyboardButton('🔆 சன் டிவி 🔆', url='https://t.me/+56ze8w46Xj4zYjNl')],
                [InlineKeyboardButton('🎭 ஜி தமிழ் 🎭', url='https://t.me/+VdExpPLNSLVlMTdl'), InlineKeyboardButton('♻️ CWC Tamil ♻️', url='https://t.me/+EPYGIZ6a035jYjBl')]
            ]
        )
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
        return

    else:
        # Send verification message if user is not verified
        if IS_VERIFY and not verify_status['is_verified']:
            short_url = "publicearn.com"
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await update_verify_status(id, verify_token=token, link="")
            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/{client.username}?start=verify_{token}')
            btn = [
                [InlineKeyboardButton("𝐂𝐥𝐢𝐜𝐤 𝐇𝐞𝐫𝐞", url=link)],
                [InlineKeyboardButton('𝐇𝐨𝐰 𝐓𝐨 𝐨𝐩𝐞𝐧 𝐭𝐡𝐢𝐬 𝐥𝐢𝐧𝐤', url=TUT_VID)]
            ]
            await message.reply(f"Your Ads token is expired, refresh your token and try again. \n\nToken Timeout: <b>{get_exp_time(get_time_until_midnight())}</b>\n\n𝗪𝗵𝗮𝘁 𝗶𝘀 𝘁𝗵𝗲 𝘁𝗼𝗸𝗲𝗻?\n\n𝗧𝗵𝗶𝘀 𝗶𝘀 𝗮𝗻 𝗮𝗱𝘀 𝘁𝗼𝗸𝗲𝗻. 𝗜𝗳 𝘆𝗼𝘂 𝗽𝗮𝘀𝘀 𝟭 𝗮𝗱, 𝘆𝗼𝘂 𝗰𝗮𝗻 𝘂𝘀𝗲 𝘁𝗵𝗲 𝗯𝗼𝘁 𝘂𝗻𝘁𝗶𝗹 𝟭𝟮 𝗔𝗠.", reply_markup=InlineKeyboardMarkup(btn), protect_content=False, quote=True)


@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [
            InlineKeyboardButton(
                "Join Channel",
                url=client.invitelink)
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='Now Click Here',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        quote=True
    )

# The remaining function definitions for `react_msg` and other dependencies should be included here.

if __name__ == "__main__":
    app = Bot()
    app.run()

    
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

    
@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>Broadcast Completed</u>

    
Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()

@Bot.on_message(filters.all)
async def react_msg(client,message):
    emojis = [
        "👍",
        "👎",
        "❤️",
        "🔥",
        "🥰",
        "👏",
        "😁",
        "🤔",
        "😱",
        "🎉",
        "🤩",
        "🙏",
        "👌",
        "🕊",
        "🤡",
        "🥱",
        "😍",
        "🐳",
        "❤‍🔥",
        "🌚",
        "🌭",
        "💯",
        "🤣",
        "⚡️",
        "🏆",
        "💔",
        "🤨",
        "😐",
        "🍓",
        "🍾",
        "💋",
        "😈",
        "😴",
        "🤓",
        "👻",
        "👨‍💻",
        "👀",
        "🙈",
        "😇",
        "🤝",
        "✍️",
        "🤗",
        "🎅",
        "🎄",
        "☃️",
        "💅",
        "🤪",
        "🗿",
        "🆒",
        "💘",
        "🙉",
        "🦄",
        "😘",
        "💊",
        "🙊",
        "😎",
        "😀",
        "😃",
        "😄",
        "😁",
        "😆",
        "😅",
        "😂",
        "🤣",
        "☺️",
        "😊",
        "😇",
        "🙂",
        "🙃",
        "😉",
        "😌",
        "😍",
        "🥰",
        "😘",
        "😗",
        "😙",
        "😚",
        "😋",
        "😛",
        "😝",
        "😜",
        "🤪",
        "🤨",
        "🧐",
        "🤓",
        "😎",
        "🤩",
        "🥳",
        "🙂‍↕️",
        "😏",
        "😒",
        "🙂‍↔️",
        "😞",
        "😔",
        "😟",
        "😕",
        "🙁",
        "☹️",
        "😣",
        "😖",
        "😫",
        "😩",
        "🥺",
        "😢",
        "😭",
        "😮‍💨",
        "😤",
        "😠",
        "😡",
        "🤬",
        "🤯",
        "😳",
        "🥵",
        "🥶",
        "😱",
        "😨",
        "😰",
        "😥",
        "😓",
        "🤗",
        "🤔",
        "🤭",
        "🤫",
        "🤥",
        "😶",
        "😶‍🌫️",
        "😐",
        "😑",
        "😬",
        "🙄",
        "😯",
        "😦",
        "😧",
        "😮",
        "😲",
        "🥱",
        "😴",
        "🤤",
        "😪",
        "😵",
        "😵‍💫",
        "🤐",
        "🥴",
        "🤢",
        "🤧",
        "😷",
        "🤒",
        "🤕",
        "🤑",
        "🤠",
        "😈",
        "👿",
        "👹",
        "👺",
        "🤡",
        "💩",
        "👻",
        "💀",
        "☠️",
        "👽",
        "👾",
        "🤖",
        "🎃",
        "😺",
        "😸",
        "😹",
        "😻",
        "😼",
        "😽",
        "🙀",
        "😿",
        "😾",
        "💘",
        "💖",
        "💝",
    ]
    rnd_emoji = random.choice(emojis)
    await client.send_reaction(
        chat_id=message.chat.id, message_id=message.id, emoji=rnd_emoji, big=True
    )
    return
