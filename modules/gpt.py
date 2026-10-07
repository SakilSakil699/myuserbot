from pyrogram import filters
from config import BOT_PREFIX as PREFIX
import os, aiohttp

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def register(app):
    @app.on_message(cmd("ai"))
    async def ai(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.ai question</code>")
        if not OPENAI_KEY:
            return await message.edit("❌ OPENAI_API_KEY missing in .env")
        await message.edit("🤖 Thinking...")
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": args[1]}],
            "max_tokens": 500
        }
        headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
        async with aiohttp.ClientSession() as s:
            async with s.post("https://api.openai.com/v1/chat/completions",
                              json=payload, headers=headers) as r:
                data = await r.json()
        try:
            reply = data["choices"][0]["message"]["content"]
            await message.edit(f"🤖 <b>AI:</b>\n\n{reply}")
        except:
            await message.edit(f"❌ API error: <code>{str(data)[:200]}</code>")
