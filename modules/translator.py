from pyrogram import filters
from config import BOT_PREFIX as PREFIX
import aiohttp

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def register(app):
    @app.on_message(cmd("tr"))
    async def translate(client, message):
        args = message.text.split(None, 2)
        if len(args) < 3:
            return await message.edit("⚠️ <code>.tr hi Hello world</code>")
        lang, text = args[1], args[2]
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "auto", "tl": lang, "dt": "t", "q": text}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params) as r:
                data = await r.json()
        try:
            out = "".join(seg[0] for seg in data[0])
            await message.edit(f"🌐 <b>[{lang}]</b>\n{out}")
        except:
            await message.edit("❌ Translation failed.")
