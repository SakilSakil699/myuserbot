"""
❤️ Auto-React — Owner ke messages pe react karo
"""

from pyrogram import filters
from helpers import cmd
from database import DB
import random

db = DB("autoreact")

REACTIONS = ["❤️", "🔥", "👍", "😂", "🎉", "⚡", "💯", "🤯"]


def register(app):

    @app.on_message(cmd("autoreact"))
    async def toggle(client, message):
        cid = message.chat.id
        args = message.text.split()

        if len(args) > 1 and args[1] == "off":
            db.delete(cid)
            return await message.edit("🛑 <b>Auto-react OFF</b>")

        db.set(cid, True)
        await message.edit("❤️ <b>Auto-react ON</b>\nAb owner ke messages pe random react hoga.")


    @app.on_message(cmd("react"))
    async def manual_react(client, message):
        """Manually react to a replied message."""
        if not message.reply_to_message:
            return await message.edit("⚠️ Reply to a message.")

        emoji = "❤️"
        args = message.text.split(None, 1)
        if len(args) > 1:
            emoji = args[1].strip()

        try:
            await client.send_reaction(
                chat_id=message.chat.id,
                message_id=message.reply_to_message.id,
                emoji=emoji,
            )
            await message.delete()
        except Exception as e:
            await message.edit(f"❌ Failed: <code>{e}</code>")
