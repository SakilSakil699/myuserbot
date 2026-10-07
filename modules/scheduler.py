from pyrogram import filters
from config import PREFIX
import asyncio, re

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def parse_time(s):
    m = re.match(r"^(\d+)([smh])$", s)
    if not m: return None
    n, u = int(m.group(1)), m.group(2)
    return n * {"s":1, "m":60, "h":3600}[u]

def register(app):
    @app.on_message(cmd("schedule"))
    async def sched(client, message):
        args = message.text.split(None, 2)
        if len(args) < 3:
            return await message.edit("⚠️ <code>.schedule 5m Hello world</code>")
        secs = parse_time(args[1])
        if not secs:
            return await message.edit("❌ Time format: 10s, 5m, 2h")
        text = args[2]
        chat = message.chat.id
        await message.edit(f"⏰ Scheduled in {args[1]}")

        async def job():
            await asyncio.sleep(secs)
            try: await client.send_message(chat, text)
            except: pass
        asyncio.create_task(job())