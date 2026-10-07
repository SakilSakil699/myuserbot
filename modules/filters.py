from pyrogram import filters as flt
from config import BOT_PREFIX as PREFIX
import json, os

F_FILE = "filters.json"

def load():
    if os.path.exists(F_FILE):
        with open(F_FILE) as f: return json.load(f)
    return {}

def save(d):
    with open(F_FILE, "w") as f: json.dump(d, f, ensure_ascii=False, indent=2)

def cmd(name):
    return flt.command(name, prefixes=PREFIX) & flt.me

def register(app):
    filters_db = load()

    @app.on_message(cmd("filter"))
    async def add_filter(client, message):
        args = message.text.split(None, 2)
        if len(args) < 3:
            return await message.edit("⚠️ <code>.filter keyword reply text</code>")
        key, reply = args[1].lower(), args[2]
        filters_db[key] = {"reply": reply, "chat": message.chat.id}
        save(filters_db)
        await message.edit(f"✅ Filter added: <code>{key}</code>")

    @app.on_message(cmd("stop"))
    async def del_filter(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.stop keyword</code>")
        key = args[1].lower()
        if key in filters_db:
            del filters_db[key]
            save(filters_db)
            await message.edit(f"🗑 Removed <code>{key}</code>")
        else:
            await message.edit("❌ Not found.")

    @app.on_message(cmd("filters"))
    async def list_filters(client, message):
        if not filters_db:
            return await message.edit("📭 No filters.")
        txt = "📋 <b>Filters:</b>\n" + "\n".join(f"• <code>{k}</code>" for k in filters_db)
        await message.edit(txt)

    @app.on_message(flt.text & ~flt.me, group=30)
    async def reply_filter(client, message):
        if not message.text: return
        text = message.text.lower()
        for key, val in filters_db.items():
            if key in text:
                try:
                    await message.reply(val["reply"])
                except: pass
                break
