from pyrogram import filters
from config import OWNER_ID
from helpers import cmd
from database import DB

db = DB("antidelete")

def register(app):
    @app.on_message(cmd("antidelete"))
    async def toggle(client, message):
        cid = message.chat.id
        args = message.text.split()
        if len(args) > 1 and args[1] == "off":
            db.delete(cid)
            return await message.edit("🛑 Anti-delete OFF")
        db.set(cid, True)
        await message.edit("🛡 Anti-delete ON (deleted msgs owner ko jayenge)")

    @app.on_message(filters.group | filters.private, group=100)
    async def logger(client, message):
        if not db.get(message.chat.id): return
        if not message.from_user: return
        # Save message in memory cache
        key = f"msg_{message.chat.id}_{message.id}"
        data = {
            "chat": message.chat.title or "Private",
            "user": message.from_user.first_name,
            "uid": message.from_user.id,
            "text": message.text or message.caption or "[media]",
        }
        db.set(key, data)

    @app.on_deleted_messages()
    async def on_del(client, messages):
        for msg in messages:
            key = f"msg_{msg.chat.id}_{msg.id}"
            data = db.get(key)
            if not data: continue
            txt = (f"🗑 <b>Deleted Message</b>\n"
                   f"<b>Chat:</b> {data['chat']}\n"
                   f"<b>User:</b> {data['user']} (<code>{data['uid']}</code>)\n"
                   f"<b>Text:</b> {data['text']}")
            try: await client.send_message(OWNER_ID, txt)
            except: pass
            db.delete(key)