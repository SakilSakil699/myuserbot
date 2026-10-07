from pyrogram import filters
from config import PREFIX
from pyrogram.handlers import MessageHandler
import asyncio

AD = {}  # {chat_id: seconds}

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def register(app):
    @app.on_message(cmd("autodel"))
    async def set_ad(client, message):
        args = message.text.split()
        if len(args) < 2:
            return await message.edit("⚠️ Usage: <code>.autodel 10</code> (seconds, 0 = off)")
        try:
            sec = int(args[1])
        except:
            return await message.edit("❌ Number do.")
        cid = message.chat.id
        if sec == 0:
            AD.pop(cid, None)
            await message.edit("🛑 <b>Auto-delete OFF</b>")
        else:
            AD[cid] = sec
            await message.edit(f"🗑 <b>Auto-delete:</b> {sec}s")
        await asyncio.sleep(3)
        try: await message.delete()
        except: pass

    # Delete OUR messages after delay
    @app.on_message(filters.me & ~filters.command(["autodel"], prefixes=PREFIX), group=20)
    async def deleter(client, message):
        cid = message.chat.id
        if cid in AD:
            await asyncio.sleep(AD[cid])
            try: await message.delete()
            except: pass