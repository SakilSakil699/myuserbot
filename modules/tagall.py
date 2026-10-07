from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from config import BOT_PREFIX as PREFIX
import asyncio

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def register(app):
    @app.on_message(cmd("tagall"))
    async def tagall(client, message):
        if message.chat.type.name not in ("GROUP", "SUPERGROUP"):
            return await message.edit("❌ Only in groups!")
        args = message.text.split(None, 1)
        note = args[1] if len(args) > 1 else "Attention!"
        await message.delete()
        mentions, count = [], 0
        async for m in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.SEARCH):
            if m.user.is_bot or m.user.is_deleted: continue
            if m.user.username:
                mentions.append(f"@{m.user.username}")
            else:
                mentions.append(m.user.mention)
            count += 1
            if len(mentions) >= 5:
                try:
                    await client.send_message(message.chat.id,
                        f"📢 <b>{note}</b>\n\n" + " ".join(mentions))
                except: pass
                mentions = []
                await asyncio.sleep(3)
        if mentions:
            try:
                await client.send_message(message.chat.id,
                    f"📢 <b>{note}</b>\n\n" + " ".join(mentions))
            except: pass
        await client.send_message(message.chat.id, f"✅ Tagged <b>{count}</b> members.")
