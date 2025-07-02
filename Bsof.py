import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageService, MessageActionChatAddUser, MessageActionChatJoinedByLink

api_id = 22340540
api_hash = '264130c425cb6a107c99fa8c4155a078'
string_session = "1AZWarzcBuw7fs0YCeoJ_-M_0uaha8eg2EZ6I3E7z398SNcen_qj0uoLFvxbeYyl8oLh3MaCwU_4R8FAYp9PBkDUeiN7Arm0gsXFkC7TvyxX8PGuivUWnAkYKIayXy5LWwTcM4CeHuYk_Lv9XaMYBxcjDOABRzMBzHUzqTfuT8KnDsBBGjCZI_3Zfkbf2CXfovPZgkMuflBvi_rLCQ6jo-uzVmMzFZr6Za8NdJKdCvh_3iRTWcaXAe2Zv20tsYMoWmYY-fLOSVgay4ZX6XHjq1FBhoae5tPY-vcpLyuBqU46yAe9b8wtbmCtp1k7wPm70mRkpBr7yJQzct_vPLNBfi6B8MLDnrHE="

chat_id = 7824772776  # آیدی عددی گروه شما

client = TelegramClient("session", api_id, api_hash, session=string_session)

welcome_texts = ["خوش اومدی جانم", "خوش اومدی"]
thank_you_keywords = ["مرسی", "ممنون", "thanks", "thank you", "tnx", "tnq", "❤️", "🙏", "😍"]

welcomed_users = {}  # کلید: (chat_id, user_id) مقدار: پیام خوش آمد (message id)
thanked_users = set()  # برای جلوگیری از پاسخ چندباره به تشکر کاربر

async def check_new_joins():
    async for message in client.iter_messages(chat_id, limit=50):
        if not isinstance(message, MessageService):
            continue
        action = message.action
        if not action:
            continue
        if isinstance(action, (MessageActionChatAddUser, MessageActionChatJoinedByLink)):
            user_ids = []
            if hasattr(action, 'users'):
                user_ids = action.users
            elif hasattr(action, 'user_id'):
                user_ids = [action.user_id]
            for user_id in user_ids:
                key = (chat_id, user_id)
                if key in welcomed_users:
                    continue  # قبلاً خوش آمد گفته شده
                user = await client.get_entity(user_id)
                welcome = welcome_texts[0] if (hash(user_id) % 2 == 0) else welcome_texts[1]
                if user.username:
                    sent = await client.send_message(chat_id, f"{welcome} @{user.username}")
                else:
                    name = user.first_name or "دوست عزیز"
                    sent = await client.send_message(chat_id, f"{welcome} [{name}](tg://user?id={user.id})", link_preview=False)
                welcomed_users[key] = sent.id

@client.on(events.NewMessage(chats=chat_id))
async def reply_to_thank_you(event):
    # باید پیام ری‌پلای باشد
    if not event.is_reply or not event.message:
        return

    user = event.sender
    key = (chat_id, user.id)
    original_msg = await event.get_reply_message()

    # بررسی اینکه پیام ریپلای شده، پیام خوش آمدگویی ربات است
    if key not in welcomed_users:
        return

    if welcomed_users[key] != original_msg.id:
        return

    if user.id in thanked_users:
        return  # قبلاً تشکر کرده و پاسخ داده شده

    text = event.raw_text.lower()
    if any(k in text for k in thank_you_keywords):
        await event.reply("☺️ معرفی کن خودتو")
        thanked_users.add(user.id)  # ثبت که جواب داده شده

async def main():
    await client.start()
    print("[✓] ربات روشن و آماده‌ست")
    while True:
        try:
            await check_new_joins()
        except Exception as e:
            print(f"خطا در خواندن ورود اعضا: {e}")
        await asyncio.sleep(30)  # هر ۳۰ ثانیه بررسی شود

if __name__ == "__main__":
    asyncio.run(main())