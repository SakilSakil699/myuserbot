from pyrogram import filters
from config import BOT_PREFIX as PREFIX
from pyrogram.enums import ChatType
import asyncio

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def register(app):
    @app.on_message(cmd("broadcast"))
    async def bc(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2 and not message.reply_to_message:
            return await message.edit("⚠️ <code>.broadcast text</code> or reply to a msg.")
        text = args[1] if len(args) > 1 else message.reply_to_message.text
        await message.edit("📡 Broadcasting...")
        sent = failed = 0
        async for dialog in client.get_dialogs():
            if dialog.chat.type in (ChatType.PRIVATE, ChatType.BOT):
                continue
            try:
                await client.send_message(dialog.chat.id, text)
                sent += 1
                await asyncio.sleep(1.5)  # ban-safe delay
            except:
                failed += 1
        await message.edit(f"✅ <b>Sent:</b> {sent}\n❌ <b>Failed:</b> {failed}")
