import asyncio
import base64
import logging
import os
import random
import re
import string
import time

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
    VERIFY_EXPIRE,
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

"""add time im seconds for waitingwaiting before delete 
1min=60, 2min=60×2=120, 5min=60×5=300"""
SECONDS = int(os.getenv("SECONDS", "600"))

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    OWNER_ID = ADMINS  # Fetch the owner's ID from config

    # Check if the user is the owner
    if id == OWNER_ID:
        # Owner-specific actions
        # You can add any additional actions specific to the owner here
        await message.reply("ʏᴏᴜ ᴀʀᴇ ᴛʜᴇ ᴏᴡɴᴇʀ! ᴀᴅᴅɪᴛɪᴏɴᴀʟ ᴀᴄᴛɪᴏɴs ᴄᴀɴ ʙᴇ ᴀᴅᴅᴇᴅ ʜᴇʀᴇ.")

    else:
        if not await present_user(id):
            try:
                await add_user(id)
            except:
                pass

        verify_status = await get_verify_status(id)
        if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
            await update_verify_status(id, is_verified=False)

        if "verify_" in message.text:
            _, token = message.text.split("_", 1)
            if verify_status['verify_token'] != token:
                return await message.reply("ʏᴏᴜʀ ᴛᴏᴋᴇɴ ɪs ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ. ᴛʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ /start")
            await update_verify_status(id, is_verified=True, verified_time=time.time())
            if verify_status["link"] == "":
                reply_markup = None
            await message.reply(f"ʏᴏᴜʀ ᴛᴏᴋᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ ᴀɴᴅ ᴠᴀʟɪᴅ ғᴏʀ: 12 ʜᴏᴜʀ", reply_markup=reply_markup, protect_content=False, quote=True)

        elif len(message.text) > 7 and verify_status['is_verified']:
            try:
                base64_string = message.text.split(" ", 1)[1]
            except:
                return
            _string = await decode(base64_string)
            argument = _string.split("-")
            if len(argument) == 3:
                try:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                except:
                    return
                if start <= end:
                    ids = range(start, end+1)
                else:
                    ids = []
                    i = start
                    while True:
                        ids.append(i)
                        i -= 1
                        if i < end:
                            break
            elif len(argument) == 2:
                try:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                except:
                    return
            temp_msg = await message.reply("Wait A Second...")
            try:
                messages = await get_messages(client, ids)
            except:
                await message.reply_text("Something went wrong..!")
                return
            await temp_msg.delete()
            
            snt_msgs = []
            
            for msg in messages:
                if bool(CUSTOM_CAPTION) & bool(msg.document):
                    caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name)
                else:
                    caption = "" if not msg.caption else msg.caption.html

                if DISABLE_CHANNEL_BUTTON:
                    reply_markup = msg.reply_markup
                else:
                    reply_markup = None

                try:
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    await asyncio.sleep(0.5)
                    snt_msgs.append(snt_msg)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    snt_msgs.append(snt_msg)
                except:
                    pass

            SD = await message.reply_text("Friends! Files will be deleted After 10min. Save them to the Saved Message now!")
            await asyncio.sleep(SECONDS)
            


            for snt_msg in snt_msgs:
                try:
                    await snt_msg.delete()
                    await SD.delete()
                except:
                    pass
           await react_msg(client, message)
           return


        elif verify_status['is_verified']:
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("• ᴀʙᴏᴜᴛ ᴍᴇ", callback_data="about"),
                  InlineKeyboardButton("ᴄʟᴏsᴇ •", callback_data="close")]]
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
            await react_msg(client, message)
            return


        else:
            verify_status = await get_verify_status(id)
            if IS_VERIFY and not verify_status['is_verified']:
                short_url = f"publicearn.com"
                TUT_VID = f"https://telegram.me/demoshort/45"
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                await update_verify_status(id, verify_token=token, link="")
                link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API,f'https://telegram.dog/{client.username}?start=verify_{token}')
                btn = [
                    [InlineKeyboardButton("𝐂𝐥𝐢𝐜𝐤 𝐇𝐞𝐫𝐞", url=link)],
                    [InlineKeyboardButton('𝐇𝐨𝐰 𝐓𝐨 𝐨𝐩𝐞𝐧 𝐭𝐡𝐢𝐬 𝐥𝐢𝐧𝐤', url=TUT_VID)]
                ]
                await message.reply(f"𝐘𝐨𝐮𝐫 𝐀𝐝𝐬 𝐭𝐨𝐤𝐞𝐧 𝐢𝐬 𝐞𝐱𝐩𝐢𝐫𝐞𝐝, 𝐫𝐞𝐟𝐫𝐞𝐬𝐡 𝐲𝐨𝐮𝐫 𝐭𝐨𝐤𝐞𝐧 𝐚𝐧𝐝 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧. \n\n𝐓𝐨𝐤𝐞𝐧 𝐓𝐢𝐦𝐞𝐨𝐮𝐭: {get_exp_time(VERIFY_EXPIRE)}\n\n𝐖𝐡𝐚𝐭 𝐢𝐬 𝐭𝐡𝐞 𝐭𝐨𝐤𝐞𝐧?\n\n𝐓𝐡𝐢𝐬 𝐢𝐬 𝐚𝐧 𝐚𝐝𝐬 𝐭𝐨𝐤𝐞𝐧. 𝐈𝐟 𝐲𝐨𝐮 𝐩𝐚𝐬𝐬 𝟏 𝐚𝐝, 𝐲𝐨𝐮 𝐜𝐚𝐧 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐟𝐨𝐫 12 𝐇𝐨𝐮𝐫 𝐚𝐟𝐭𝐞𝐫 𝐩𝐚𝐬𝐬𝐢𝐧𝐠 𝐭𝐡𝐞 𝐚𝐝.", reply_markup=InlineKeyboardMarkup(btn), protect_content=False, quote=True)
                

    
        
#=====================================================================================##

WAIT_MSG = """"<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message with out any spaces.</code>"""

#=====================================================================================##

    
    
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    buttons = [
        [
            InlineKeyboardButton(
                "• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •",
                url = client.invitelink)
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text = '• ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •',
                    url = f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text = FORCE_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
        reply_markup = InlineKeyboardMarkup(buttons),
        quote = True,
        disable_web_page_preview = True
    )
    await react_msg(client, message)
    return

    
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
        "❤️‍🔥",
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
        "🫡",
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
    ]
    rnd_emoji = random.choice(emojis)
    await client.send_reaction(
        chat_id=message.chat.id, message_id=message.id, emoji=rnd_emoji, big=True
    )
    return
