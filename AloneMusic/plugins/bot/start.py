import time

from py_yt import VideosSearch
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from AloneMusic import app
from AloneMusic.misc import _boot_
from AloneMusic.plugins.sudo.sudoers import sudoers_list
from AloneMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from AloneMusic.utils.decorators.language import LanguageStart
from AloneMusic.utils.formatters import get_readable_time
from AloneMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string


# 🔥 PREMIUM START (Channel Copy Method)
PREMIUM_START_CHANNEL = config.START_CHANNEL_ID
PREMIUM_START_MSG_ID = config.START_MESSAGE_ID


# =================================================
# PRIVATE START
# =================================================

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):

    await add_served_user(message.from_user.id)
    await message.react("🍓")

    # ================= PARAM HANDLING =================

    if len(message.text.split()) > 1:
        param = message.text.split(None, 1)[1]

        # HELP PANEL
        if param.startswith("help"):
            keyboard = help_pannel(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                has_spoiler=True,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        # SUDO LIST
        if param.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            return

        # TRACK INFO
        if param.startswith("inf"):
            m = await message.reply_text("🔎 Searching...")

            query = param.replace("info_", "", 1)
            results = VideosSearch(
                f"https://www.youtube.com/watch?v={query}",
                limit=1,
            )
            data = (await results.next())["result"][0]

            searched_text = _["start_6"].format(
                data["title"],
                data["duration"],
                data["viewCount"]["short"],
                data["publishedTime"],
                data["channel"]["link"],
                data["channel"]["name"],
                app.mention,
            )

            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=_["S_B_8"], url=data["link"]
                        ),
                        InlineKeyboardButton(
                            text=_["S_B_9"], url=config.SUPPORT_CHAT
                        ),
                    ]
                ]
            )

            await m.delete()

            return await app.send_photo(
                chat_id=message.chat.id,
                photo=data["thumbnails"][0]["url"].split("?")[0],
                has_spoiler=True,
                caption=searched_text,
                reply_markup=buttons,
            )

    # ================= DEFAULT PREMIUM START =================

    buttons = InlineKeyboardMarkup(private_panel(_))

    await app.copy_message(
        chat_id=message.chat.id,
        from_chat_id=PREMIUM_START_CHANNEL,
        message_id=PREMIUM_START_MSG_ID,
        reply_markup=buttons,
    )

    if await is_on_off(2):
        await app.send_message(
            chat_id=config.LOGGER_ID,
            text=(
                f"{message.from_user.mention} started the bot.\n\n"
                f"<b>User ID:</b> <code>{message.from_user.id}</code>\n"
                f"<b>Username:</b> @{message.from_user.username}"
            ),
        )


# =================================================
# GROUP START
# =================================================

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):

    uptime = int(time.time() - _boot_)
    buttons = InlineKeyboardMarkup(start_panel(_))

    await message.reply_photo(
        photo=config.START_IMG_URL,
        has_spoiler=True,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=buttons,
    )

    await add_served_chat(message.chat.id)


# =================================================
# WELCOME HANDLER
# =================================================

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):

    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            # Ban if banned user joins
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            # If bot added
            if member.id == app.id:

                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                buttons = InlineKeyboardMarkup(start_panel(_))

                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    has_spoiler=True,
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=buttons,
                )

                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as ex:
            print(ex)