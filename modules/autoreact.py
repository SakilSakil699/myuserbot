from pyrogram import filters
from pyrogram.types import ReactionTypeEmoji
from helpers import cmd
import random

REACTIONS = ["❤️", "🔥", "👍", "😂", "🤯", "🎉", "⚡"]

def register(app):
    @app.on_message(cmd("autoreact"))
    async def toggle(client, message):
        cid = message.chat.id
        args = message.text.split()
        from database import DB
        db = DB("autoreact")
        if len(args) > 1 and args[1] == "off":
            db.delete(cid); return await message.edit("🛑 OFF")
        db.set(cid, True)
        await message.edit("❤️ Auto-react ON")

    # Auto-react on OWN messages? No — react on others
    # NOTE: Telegram API only allows reaction via send_reaction