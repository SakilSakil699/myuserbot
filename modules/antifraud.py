from pyrogram import filters
from database import DB
import re

db = DB("antifraud")
SUSPICIOUS = [
    r"bit\.ly", r"tinyurl\.com", r"t\.me/joinchat",
    r"free.*crypto", r"double.*money", r"@.*admin.*verify",
    r"click.*here.*prize", r"telegram.*premium.*free",
]

def register(app):
    @app.on_message(filters.command("antifraud") & filters.me)
    async def toggle(client, message):
        cid = message.chat.id
        args = message.text.split()
        if len(args) > 1 and args[1] == "off":
            db.delete(cid)
            return await message.edit("🛑 Anti-fraud OFF")
        db.set(cid, True)
        await message.edit("🛡 Anti-fraud ON")

    @app.on_message(filters.group & filters.text & ~filters.me, group=50)
    async def watch(client, message):
        if not db.get(message.chat.id): return
        text = message.text.lower()
        for pattern in SUSPICIOUS:
            if re.search(pattern, text):
                try:
                    await message.delete()
                    await client.send_message(message.chat.id,
                        f"🚨 <b>Suspicious link removed!</b>\n{message.from_user.mention}, ye scam jaisa lag raha hai.")
                except: pass
                return