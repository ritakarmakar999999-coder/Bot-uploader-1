# 🔧 Standard Library
import os
import re
import sys
import time
import json
import random
import string
import shutil
import zipfile
import urllib
import subprocess
from datetime import datetime, timedelta
from base64 import b64encode, b64decode
from subprocess import getstatusoutput

# 🕒 Timezone
import pytz

# 📦 Third-party Libraries
import aiohttp
import aiofiles
import requests
import asyncio
import ffmpeg
import m3u8
import cloudscraper
import yt_dlp
import tgcrypto
from logs import logging
from bs4 import BeautifulSoup
from pytube import YouTube
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ⚙️ Pyrogram
from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)
from pyrogram.errors import (
    FloodWait,
    BadRequest,
    Unauthorized,
    SessionExpired,
    AuthKeyDuplicated,
    AuthKeyUnregistered,
    ChatAdminRequired,
    PeerIdInvalid,
    RPCError
)
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

# 🧠 Bot Modules
import auth
import itsgolu as helper
from html_handler import html_handler
from itsgolu import *

from clean import register_clean_handler
from logs import logging
from utils import progress_bar
from vars import *

# Pyromod fix
import pyromod.listen
pyromod.listen.Client.listen = pyromod.listen.listen

from db import db

auto_flags = {}
auto_clicked = False

# Global variables
watermark = "/d"
count = 0
userbot = None
timeout_duration = 300


# Initialize bot
bot = Client(
    "ugx",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=300,
    sleep_threshold=60,
    in_memory=True
)

register_clean_handler(bot)


@bot.on_message(filters.command("start") & (filters.private | filters.channel))
async def start(bot: Client, m: Message):
    try:
        if m.chat.type == "channel":
            await m.reply_text(
                "**✨ Bot is active in this channel**\n\n"
                "**Available Commands:**\n"
                "• /drm\n"
                "• /plan\n"
            )
        else:
            await m.reply_photo(
                photo=photologo,
                caption=f"**Commands for [{m.from_user.first_name}]**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Features", callback_data="features"),
                            InlineKeyboardButton("Details", callback_data="details")
                        ]
                    ]
                )
            )
    except Exception as e:
        print(e)


def auth_check_filter(_, client, message):
    return True


auth_filter = filters.create(auth_check_filter)


@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    await message.reply_text(f"`{message.chat.id}`")


@bot.on_message(filters.command(["t2h"]))
async def call_html_handler(bot: Client, message: Message):
    await html_handler(bot, message)


@bot.on_message(filters.command(["logs"]) & auth_filter)
async def send_logs(client: Client, m: Message):
    try:
        with open("logs.txt", "rb") as file:
            sent = await m.reply_text("Sending logs...")
            await m.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await m.reply_text(str(e))
        @bot.on_message(filters.command(["drm"]) & auth_filter)
async def txt_handler(bot: Client, m: Message):

    bot_info = await bot.get_me()
    bot_username = bot_info.username

    editable = await m.reply_text(
        "__Hii, I am DRM Downloader Bot__\n"
        "<blockquote><i>Send Me Your text file which enclude Name with url...\n"
        "E.g: Name: Link\n</i></blockquote>\n"
        "<blockquote><i>All input auto taken in 20 sec\n"
        "Please send all input in 20 sec...\n</i></blockquote>"
    )

    input: Message = await bot.listen(editable.chat.id)

    if not input.document:
        await m.reply_text("<b>❌ Please send a text file!</b>")
        return

    if not input.document.file_name.endswith('.txt'):
        await m.reply_text("<b>❌ Please send a .txt file!</b>")
        return

    x = await input.download()
    await input.delete(True)

    file_name, ext = os.path.splitext(os.path.basename(x))
    path = f"./downloads/{m.chat.id}"

    pdf_count = 0
    img_count = 0
    v2_count = 0
    mpd_count = 0
    m3u8_count = 0
    yt_count = 0
    drm_count = 0
    zip_count = 0
    other_count = 0

    try:
        with open(x, "r", encoding="utf-8") as f:
            content = f.read()

        content = content.split("\n")
        content = [line.strip() for line in content if line.strip()]

        links = []
        for i in content:
            if "://" in i:
                parts = i.split("://", 1)
                name = parts[0]
                url = parts[1]
                links.append([name, url])

                if ".pdf" in url:
                    pdf_count += 1
                elif url.endswith((".png", ".jpeg", ".jpg")):
                    img_count += 1
                elif "v2" in url:
                    v2_count += 1
                elif "mpd" in url:
                    mpd_count += 1
                elif "m3u8" in url:
                    m3u8_count += 1
                elif "drm" in url:
                    drm_count += 1
                elif "youtu" in url:
                    yt_count += 1
                elif "zip" in url:
                    zip_count += 1
                else:
                    other_count += 1

    except Exception as e:
        await m.reply_text(f"File read error: {e}")
        os.remove(x)
        return

    await editable.edit(
        f"**Total 🔗 links found are {len(links)}\n"
        f"PDF : {pdf_count} | IMG : {img_count} | V2 : {v2_count}\n"
        f"ZIP : {zip_count} | DRM : {drm_count} | M3U8 : {m3u8_count}\n"
        f"MPD : {mpd_count} | YT : {yt_count}\n"
        f"OTHERS : {other_count}\n\n"
        f"Send Your Index File ID Between 1-{len(links)}**"
    )

    try:
        input0: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text = input0.text
        await input0.delete(True)
    except asyncio.TimeoutError:
        raw_text = "1"

    if int(raw_text) > len(links):
        await editable.edit("Invalid index range")
        return
        await editable.edit("**1. Enter Batch Name\n2. Send /d For TXT Batch Name**")
    try:
        input1: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text0 = input1.text
        await input1.delete(True)
    except asyncio.TimeoutError:
        raw_text0 = "/d"

    if raw_text0 == "/d":
        b_name = file_name.replace("_", " ")
    else:
        b_name = raw_text0

    await editable.edit(
        "**🎞️  Enter Resolution**\n"
        "`360` | `480` | `720` | `1080`"
    )
    try:
        input2: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text2 = input2.text
        await input2.delete(True)
    except asyncio.TimeoutError:
        raw_text2 = "480"

    if raw_text2 == "360":
        res = "640x360"
    elif raw_text2 == "480":
        res = "854x480"
    elif raw_text2 == "720":
        res = "1280x720"
    elif raw_text2 == "1080":
        res = "1920x1080"
    else:
        res = "UN"

    await editable.edit("**Send watermark text or /d**")
    try:
        inputx: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_textx = inputx.text
        await inputx.delete(True)
    except asyncio.TimeoutError:
        raw_textx = "/d"

    global watermark
    watermark = "/d" if raw_textx == "/d" else raw_textx

    await editable.edit("**Send credit name or /d**")
    try:
        input3: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text3 = input3.text
        await input3.delete(True)
    except asyncio.TimeoutError:
        raw_text3 = "/d"

    CR = CREDIT if raw_text3 == "/d" else raw_text3

    await editable.edit(
        "**Send thumbnail image**\n"
        "`/d` default | `/skip` skip"
    )
    thumb = "/d"
    try:
        input6 = await bot.listen(editable.chat.id, timeout=20)
        if input6.photo:
            os.makedirs("downloads", exist_ok=True)
            temp_file = f"downloads/thumb_{m.from_user.id}.jpg"
            await bot.download_media(input6.photo, temp_file)
            thumb = temp_file
        elif input6.text in ["/d", "/skip"]:
            thumb = input6.text
        await input6.delete(True)
    except asyncio.TimeoutError:
        thumb = "/d"

    await editable.edit("**Send Channel ID or /d**")
    try:
        input7: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text7 = input7.text
        await input7.delete(True)
    except asyncio.TimeoutError:
        raw_text7 = "/d"

    channel_id = m.chat.id if raw_text7 == "/d" else raw_text7
    await editable.delete()

    failed_count = 0
    count = int(raw_text)
    try:
        for i in range(int(raw_text) - 1, len(links)):
            Vxy = links[i][1].replace("file/d/", "uc?export=download&id=")
            url = "https://" + Vxy if not Vxy.startswith("http") else Vxy

            name1 = re.sub(r'[\\/*?:"<>|]', "", links[i][0]).strip()
            name1 = name1.replace(" ", "_")
            name = name1[:60]

            Show = (
                f"<i><b>📥 Fast Video Downloading</b></i>\n"
                f"<blockquote><b>{str(count).zfill(3)}) {name1}</b></blockquote>"
            )
            prog = await bot.send_message(channel_id, Show)

            try:
                cmd = f'yt-dlp -f "b[height<={raw_text2}]" "{url}" -o "{name}.mp4"'
                res_file = await helper.download_video(url, cmd, name)

                if res_file:
                    await helper.send_vid(
                        bot,
                        m,
                        cc,
                        res_file,
                        thumb,
                        name,
                        prog,
                        channel_id,
                        watermark=watermark
                    )
                    count += 1
                else:
                    failed_count += 1

                await prog.delete()

            except Exception as e:
                try:
                    await bot.send_message(
                        channel_id,
                        f"⚠️**Downloading Failed**⚠️\n"
                        f"**Name:** `{str(count).zfill(3)} {name1}`\n"
                        f"**Error:** `{e}`"
                    )
                except:
                    await m.reply_text(str(e))

                failed_count += 1
                count += 1
                continue

    except Exception as e:
        await m.reply_text(str(e))
        success_count = len(links) - failed_count
    video_count = v2_count + mpd_count + m3u8_count + yt_count + drm_count + zip_count + other_count

    if raw_text7 == "/d":
        await bot.send_message(
            channel_id,
            (
                "<b>📬 PROCESS COMPLETED</b>\n\n"
                f"<blockquote><b>📚 Batch Name :</b> {b_name}</blockquote>\n\n"
                "╭────────────────\n"
                f"├ 🔗 Total URLs : <code>{len(links)}</code>\n"
                f"├ ✅ Successful : <code>{success_count}</code>\n"
                f"├ ❌ Failed : <code>{failed_count}</code>\n"
                "╰────────────────\n\n"
                "╭──────── 📦 CATEGORY ────────\n"
                f"├ 🎞️ Videos : <code>{video_count}</code>\n"
                f"├ 📑 PDFs : <code>{pdf_count}</code>\n"
                f"├ 🖼️ Images : <code>{img_count}</code>\n"
                "╰────────────────────────────\n\n"
                "<i>Extracted by NATH 🤖</i>"
            )
        )
    else:
        await bot.send_message(
            channel_id,
            (
                "<b>-┈━═.•°✅ Completed ✅°•.═━┈-</b>\n"
                f"<blockquote><b>🎯 Batch Name : {b_name}</b></blockquote>\n"
                f"<blockquote>"
                f"🔗 Total URLs : {len(links)}\n"
                f"🟢 Successful : {success_count}\n"
                f"🔴 Failed : {failed_count}\n"
                f"</blockquote>"
            )
        )
        await bot.send_message(
            m.chat.id,
            "<blockquote><b>✅ Your task is completed. Check your set channel.</b></blockquote>"
        )


@bot.on_callback_query(filters.regex("features"))
async def features_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "**🔥 Bot Features 🔥**\n\n"
        "• DRM video download\n"
        "• Multi-format support\n"
        "• PDF / Image / Audio support\n"
        "• Custom watermark\n",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]]
        )
    )


@bot.on_callback_query(filters.regex("details"))
async def details_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "**📋 Bot Details 📋**\n\n"
        "• Name : NATH\n"
        "• Language : Python\n"
        "• Framework : Pyrogram\n",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]]
        )
    )


@bot.on_callback_query(filters.regex("back_to_start"))
async def back_to_start_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=photologo,
            caption="**Bot Ready 🚀**"
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Features", callback_data="features"),
                    InlineKeyboardButton("Details", callback_data="details")
                ]
            ]
        )
    )


print("Bot Started...")
bot.run()
