import asyncio
import random
import os
import threading
import http.server
import socketserver
import time
import sys

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import ChannelParticipantsAdmins, User, Message

api_id = 22340540
api_hash = '264130c425cb6a107c99fa8c4155a078'
string_session = "1AZWarzcBuw7fs0YCeoJ_-M_0uaha8eg2EZ6I3E7z398SNcen_qj0uoLFvxbeYyl8oLh3MaCwU_4R8FAYp9PBkDUeiN7Arm0gsXFkC7TvyxX8PGuivUWnAkYKIayXy5LWwTcM4CeHuYk_Lv9XaMYBxcjDOABRzMBzHUzqTfuT8KnDsBBGjCZI_3Zfkbf2CXfovPZgkMuflBvi_rLCQ6jo-uzVmMzFZr6Za8NdJKdCvh_3iRTWcaXAe2Zv20tsYMoWmYY-fLOSVgay4ZX6XHjq1FBhoae5tPY-vcpLyuBqU46yAe9b8wtbmCtp1k7wPm70mRkpBr7yJQzct_vPLNBfi6B8MLDnrHE="

PORT = int(os.environ.get("PORT", 8080))

def fake_webserver():
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"[✓] Fake HTTP server started at port {PORT} for Render")
        httpd.serve_forever()

def start_bot():
    client = TelegramClient(StringSession(string_session), api_id, api_hash)
    welcome_texts = ["خوش اومدی جانم", "خوش اومدی"]
    thank_you_keywords = ["مرسی", "ممنون", "thanks", "thank you", "tnx", "tnq", "❤️", "🙏", "😍"]
    welcomed_users = set()

    @client.on(events.ChatAction)
    async def welcome_new_user(event):
        if not event.user_joined and not event.user_added:
            return
        chat = await event.get_chat()
        me = await client.get_me()
        admins = await client.get_participants(chat, filter=ChannelParticipantsAdmins)
        admin_ids = {admin.id for admin in admins}
        if me.id not in admin_ids:
            return
        user: User = await event.get_user()
        msg = random.choice(welcome_texts)
        if user.username:
            sent_msg = await event.reply(f"@{user.username} {msg}")
        else:
            sent_msg = await event.reply(f"[{user.first_name}](tg://user?id={user.id}) {msg}")
        welcomed_users.add((chat.id, user.id, sent_msg.id))

    @client.on(events.NewMessage())
    async def reply_to_thank_you(event: events.NewMessage.Event):
        if not event.is_reply or not event.message:
            return
        try:
            original_msg: Message = await event.get_reply_message()
        except:
            return
        user = event.sender
        chat_id = event.chat_id
        was_welcomed = any(
            chat_id == cid and user.id == uid and original_msg.id == mid
            for (cid, uid, mid) in welcomed_users
        )
        if not was_welcomed:
            return
        msg_text = event.raw_text.lower()
        if any(k in msg_text for k in thank_you_keywords):
            await event.reply("☺️ معرفی کن خودتو")
            welcomed_users.discard((chat_id, user.id, original_msg.id))

    async def run_bot():
        await client.start()
        print(f"[✓] ربات وصل شد ({(await client.get_me()).first_name})")
        await asyncio.sleep(60)  # فقط ۶۰ ثانیه اجرا کن
        print("[!] تایم اجرا تموم شد. ری‌استارت...")
        await client.disconnect()

    client.loop.run_until_complete(run_bot())

if __name__ == "__main__":
    threading.Thread(target=fake_webserver, daemon=True).start()

    while True:
        start_bot()
        time.sleep(2)  # مکث کوتاه قبل اجرای دوباره