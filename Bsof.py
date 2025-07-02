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

def fake_webserver():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"[✓] Fake HTTP server started at port {PORT} for Render")
        httpd.serve_forever()

client = TelegramClient(StringSession(string_session), api_id, api_hash)
welcome_texts = ["خوش اومدی جانم", "خوش اومدی"]
thank_you_keywords = ["مرسی", "ممنون", "thanks", "thank you", "tnx", "tnq", "❤️", "🙏", "😍"]
welcomed_users = {}

@client.on(events.ChatAction)
async def welcome_new_user(event):
    if not (event.user_joined or event.user_added):
        return

    chat = await event.get_chat()
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

    # ذخیره اطلاعات برای پیگیری تشکر بعدی
    welcomed_users[(event.chat_id, user.id)] = sent.id

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

async def main():
    await client.start()
    print("[✓] ربات روشن و آماده‌ست")
    await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=fake_webserver, daemon=True).start()
    asyncio.run(main())