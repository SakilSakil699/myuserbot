from pyrogram import filters
from pyrogram.types import Message
from helpers import cmd
from database import DB

db = DB("welcome")

def register(app):
    @app.on_message(cmd("setwelcome"))
    async def setw(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.setwelcome Welcome {mention} to {chat}!</code>")
        db.set(message.chat.id, args[1])
        await message.edit("✅ Welcome message set!")

    @app.on_message(filters.new_chat_members & filters.group, group=70)
    async def welcome(client, message):
        template = db.get(message.chat.id)
        if not template: return
        for user in message.new_chat_members:
            if user.is_bot: continue
            txt = (template
                   .replace("{mention}", user.mention)
                   .replace("{chat}", message.chat.title)
                   .replace("{name}", user.first_name))
            try: await message.reply(txt)
            except: pass