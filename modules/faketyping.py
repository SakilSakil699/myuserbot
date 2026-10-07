from pyrogram import filters
from pyrogram.enums import ChatAction
from helpers import cmd
import asyncio

ACTIVE = set()

def register(app):
    @app.on_message(cmd("faketype"))
    async def start(client, message):
        cid = message.chat.id
        args = message.text.split()
        if len(args) > 1 and args[1] == "stop":
            ACTIVE.discard(cid)
            return await message.edit("🛑 Stopped.")
        ACTIVE.add(cid)
        await message.edit("⌨️ Fake typing ON")

        async def loop():
            while cid in ACTIVE:
                try: await client.send_chat_action(cid, ChatAction.TYPING)
                except: pass
                await asyncio.sleep(4)
        asyncio.create_task(loop())