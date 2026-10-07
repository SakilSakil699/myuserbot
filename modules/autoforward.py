from pyrogram import filters
from helpers import cmd
from database import DB
import asyncio

db = DB("autoforward")

def register(app):
    @app.on_message(cmd("autofw"))
    async def setup(client, message):
        args = message.text.split()
        if len(args) < 2:
            return await message.edit("⚠️ <code>.autofw off</code> | <code>.autofw on</code> (run from TARGET chat)")
        if args[1] == "off":
            db.delete("active")
            return await message.edit("🛑 Auto-forward OFF")
        if args[1] == "add":
            if len(args) < 3: return await message.edit("⚠️ <code>.autofw add source_chat_id</code>")
            srcs = db.get("sources", [])
            srcs.append(int(args[2]))
            db.set("sources", srcs)
            return await message.edit(f"➕ Added source: <code>{args[2]}</code>")
        if args[1] == "settarget":
            db.set("target", message.chat.id)
            return await message.edit(f"🎯 Target set: <code>{message.chat.id}</code>")
        if args[1] == "on":
            db.set("active", True)
            await message.edit("✅ Auto-forward ON")

    @app.on_message(filters.all, group=200)
    async def forwarder(client, message):
        if not db.get("active"): return
        sources = db.get("sources", [])
        target = db.get("target")
        if message.chat.id in sources and target:
            try: await message.forward(target)
            except: pass