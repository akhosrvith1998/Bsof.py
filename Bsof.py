
import os
import random
import asyncio
import threading
import http.server
import socketserver
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# اطلاعات اکانت
api_id = 22340540
api_hash = '264130c425cb6a107c99fa8c4155a078'
string_session =  "1AZWarzcBuw7fs0YCeoJ_-M_0uaha8eg2EZ6I3E7z398SNcen_qj0uoLFvxbeYyl8oLh3MaCwU_4R8FAYp9PBkDUeiN7Arm0gsXFkC7TvyxX8PGuivUWnAkYKIayXy5LWwTcM4CeHuYk_Lv9XaMYBxcjDOABRzMBzHUzqTfuT8KnDsBBGjCZI_3Zfkbf2CXfovPZgkMuflBvi_rLCQ6jo-uzVmMzFZr6Za8NdJKdCvh_3iRTWcaXAe2Zv20tsYMoWmYY-fLOSVgay4ZX6XHjq1FBhoae5tPY-vcpLyuBqU46yAe9b8wtbmCtp1k7wPm70mRkpBr7yJQzct_vPLNBfi6B8MLDnrHE="

# پورت پیش‌فرض برای اجرای fake server
PORT = int(os.environ.get("PORT", 8080))

# سرور فیک برای بیدار نگه‌داشتن سرویس روی Render
def fake_web_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"[✓] فیک‌سرور روی پورت {PORT} فعال شد")
        httpd.serve_forever()

# کلاینت تلگرام
client = TelegramClient(StringSession(string_session), api_id, api_hash)

welcome_texts = ["خوش اومدی جانم", "خوش اومدی"]
thank_you_keywords = ["مرسی", "ممنون", "thanks", "thank you", "tnx", "tnq", "❤️", "🙏", "😍"]
welcomed_users = {}

# وقتی TLProBot کسی رو تگ کرد، ما هم تگ کنیم
@client.on(events.NewMessage(from_users=620438362))
async def tlprobot_message_handler(event):
    text = event.raw_text
    entities = event.message.entities or []

    for entity in entities:
        if hasattr(entity, 'user_id'):
            user_id = entity.user_id
            name = f"[کاربر](tg://user?id={user_id})"
        else:
            offset = entity.offset
            length = entity.length
            name = text[offset:offset+length]
        msg = random.choice(welcome_texts)
        reply = await event.respond(f"{msg} {name}", link_preview=False)
        welcomed_users[(event.chat_id, reply.id)] = entity

# وقتی کاربر تشکر کرد روی ریپلای، پاسخ بدیم
@client.on(events.NewMessage())
async def reply_to_thank_you(event):
    if not event.is_reply:
        return
    original_msg = await event.get_reply_message()
    key = (event.chat_id, original_msg.id)
    if key in welcomed_users:
        if any(k in event.raw_text.lower() for k in thank_you_keywords):
            await event.reply("☺️ معرفی کن خودتو")
            del welcomed_users[key]

# اجرای اصلی
async def main():
    await client.start()
    print("[✓] ربات فعال شد و در حال بررسی پیام‌های TLProBot است")
    await client.run_until_disconnected()

# شروع فیک سرور و ربات همزمان
if __name__ == "__main__":
    threading.Thread(target=fake_web_server, daemon=True).start()
    asyncio.run(main())