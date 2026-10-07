from helpers import cmd
import asyncio, re

def parse_time(s):
    m = re.match(r"^(\d+)(s|m|h|d)$", s.lower())
    if not m: return None
    n, u = int(m.group(1)), m.group(2)
    return n * {"s":1, "m":60, "h":3600, "d":86400}[u]

def register(app):
    @app.on_message(cmd("remind"))
    async def remind(client, message):
        args = message.text.split(None, 2)
        if len(args) < 3:
            return await message.edit("⚠️ <code>.remind 10m Take medicine</code>")
        secs = parse_time(args[1])
        if not secs: return await message.edit("❌ Time: 10s, 5m, 2h, 1d")
        text = args[2]
        cid = message.chat.id
        await message.edit(f"⏰ Reminder set for {args[1]}")

        async def job():
            await asyncio.sleep(secs)
            try:
                await client.send_message(cid, f"🔔 <b>Reminder:</b>\n{text}")
            except: pass
        asyncio.create_task(job())