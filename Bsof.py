import os
import random
import threading
import http.server
import socketserver
import asyncio

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import ChannelParticipantsAdmins

api_id = 22340540
api_hash = '264130c425cb6a107c99fa8c4155a078'
string_session = "1AZWarzcBuw7fs0YCeoJ_-M_0uaha8eg2EZ6I3E7z398SNcen_qj0uoLFvxbeYyl8oLh3MaCwU_4R8FAYp9PBkDUeiN7Arm0gsXFkC7TvyxX8PGuivUWnAkYKIayXy5LWwTcM4CeHuYk_Lv9XaMYBxcjDOABRzMBzHUzqTfuT8KnDsBBGjCZI_3Zfkbf2CXfovPZgkMuflBvi_rLCQ6jo-uzVmMzFZr6Za8NdJKdCvh_3iRTWcaXAe2Zv20tsYMoWmYY-fLOSVgay4ZX6XHjq1FBhoae5tPY-vcpLyuBqU46yAe9b8wtbmCtp1k7wPm70mRkpBr7yJQzct_vPLNBfi6B8MLDnrHE="

PORT = int(os.environ.get("PORT", 8080))

ADMIN_ID = 7824772776  # عدد آیدی تلگرام خودت را اینجا قرار بده

client = TelegramClient(StringSession(string_session), api_id, api_hash)

welcome_texts = ["خوش اومدی جانم", "خوش اومدی"]
thank_you_keywords = ["مرسی", "ممنون", "thanks", "thank you", "tnx", "tnq", "❤️", "🙏", "😍"]

# فقط گروه‌هایی که توی اونها تایید شدیم
approved_chats = set()

# نگهداری پیام خوش‌آمدگویی برای تشخیص تشکر
welcomed_users = {}

@client.on(events.ChatAction)
async def welcome_new_user(event):
    chat = await event.get_chat()

    # اگر گروه هنوز تایید نشده
    if chat.id not in approved_chats:
        # لینک گروه رو به ادمین بفرست
        try:
            await client.send_message(
                ADMIN_ID,
                f"ربات تو گروه جدیدی اضافه شده:\n{chat.title}\n\n"
                f"https://t.me/c/{str(chat.id)[4:] if str(chat.id).startswith('-100') else chat.id}\n\n"
                f"برای تایید پاسخ 'شروع کن' بده."
            )
        except Exception as e:
            print(f"خطا در ارسال پیام به ادمین: {e}")
        return  # تا وقتی تایید نشه، کاری نمیکنه

    # اگر تایید شده ادامه بده
    if not (event.user_joined or event.user_added):
        return

    me = await client.get_me()
    admins = await client.get_participants(chat, filter=ChannelParticipantsAdmins)
    if me.id not in {admin.id for admin in admins}:
        return

    user = await event.get_user()
    welcome = random.choice(welcome_texts)

    if user.username:
        sent = await event.reply(f"{welcome} @{user.username}")
    else:
        name = user.first_name or "دوست عزیز"
        sent = await event.reply(f"{welcome} [{name}](tg://user?id={user.id})", link_preview=False)

    welcomed_users[(event.chat_id, user.id)] = sent.id

@client.on(events.NewMessage(from_users=ADMIN_ID))
async def admin_approval(event):
    text = event.raw_text.strip().lower()
    # انتظار دستور شروع از ادمین
    if text == "شروع کن":
        # آخرین گروهی که پیام دادیم و تایید نشده رو تایید کن
        async for dialog in client.iter_dialogs():
            chat = dialog.entity
            if chat.id not in approved_chats and chat.title:
                approved_chats.add(chat.id)
                await event.reply(f"گروه '{chat.title}' تایید شد و ربات فعال شد.")
                break

@client.on(events.NewMessage())
async def reply_to_thank_you(event):
    if not event.is_reply or not event.message:
        return

    try:
        original_msg = await event.get_reply_message()
    except:
        return

    user = event.sender
    key = (event.chat_id, user.id)

    if key in welcomed_users and welcomed_users[key] == original_msg.id:
        text = event.raw_text.lower()
        if any(k in text for k in thank_you_keywords):
            await event.reply("☺️ معرفی کن خودتو")
            del welcomed_users[key]

async def fake_webserver():
    import http.server
    import socketserver

    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"[✓] Fake HTTP server started at port {PORT} for Render")
        httpd.serve_forever()

async def main():
    threading.Thread(target=lambda: asyncio.run(fake_webserver()), daemon=True).start()
    await client.start()
    print("[✓] ربات روشن و آماده‌ست")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())