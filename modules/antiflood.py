from pyrogram import filters
from config import BOT_PREFIX as PREFIX
import time, asyncio

TRACK = {}  # {chat_id: {user_id: [timestamps]}}
ENABLED = set()

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def register(app):
    @app.on_message(cmd("antiflood"))
    async def toggle(client, message):
        cid = message.chat.id
        args = message.text.split()
        if len(args) > 1 and args[1] == "off":
            ENABLED.discard(cid)
            return await message.edit("🛑 Anti-flood OFF")
        ENABLED.add(cid)
        await message.edit("🛡 Anti-flood ON (5 msgs / 10 sec)")

    @app.on_message(filters.group & ~filters.service, group=40)
    async def watch(client, message):
        cid = message.chat.id
        if cid not in ENABLED or not message.from_user: return
        uid = message.from_user.id
        now = time.time()
        TRACK.setdefault(cid, {}).setdefault(uid, [])
        TRACK[cid][uid] = [t for t in TRACK[cid][uid] if now - t < 10]
        TRACK[cid][uid].append(now)
        if len(TRACK[cid][uid]) >= 5:
            TRACK[cid][uid] = []
            try:
                await message.delete()
                await client.restrict_chat_member(cid, uid, permissions=None)
                await client.send_message(cid, f"🚫 {message.from_user.mention} muted for flooding.")
            except: pass
