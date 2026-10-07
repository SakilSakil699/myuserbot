from pyrogram import filters
from helpers import cmd
from database import DB
import random

db = DB("chatclone")

def register(app):
    @app.on_message(cmd("learn"))
    async def learn(client, message):
        if not message.reply_to_message:
            return await message.edit("⚠️ Reply to user's message.")
        target = message.reply_to_message.from_user.id
        text = message.reply_to_message.text
        if not text: return await message.edit("❌ No text.")
        samples = db.get(target, [])
        samples.append(text)
        db.set(target, samples[-200:])
        await message.edit(f"📚 Learned ({len(samples)} samples)")

    @app.on_message(cmd("mimic"))
    async def mimic(client, message):
        if not message.reply_to_message:
            return await message.edit("⚠️ Reply to user.")
        target = message.reply_to_message.from_user.id
        samples = db.get(target, [])
        if not samples:
            return await message.edit("❌ No data. Use .learn first.")
        # Markov-ish chain
        words = " ".join(samples).split()
        out = " ".join(random.choices(words, k=min(15, len(words))))
        await message.edit(f"🤖 <b>Clone says:</b>\n{out}")