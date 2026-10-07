from helpers import cmd
from config import VIRUSTOTAL_API_KEY
import aiohttp, base64

def register(app):
    @app.on_message(cmd("scan"))
    async def scan(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.scan url</code>")
        url = args[1].strip()
        if not VIRUSTOTAL_API_KEY:
            return await message.edit("❌ VIRUSTOTAL_API_KEY missing")
        await message.edit("🔍 Scanning...")
        # Submit URL
        async with aiohttp.ClientSession() as s:
            headers = {"x-apikey": VIRUSTOTAL_API_KEY}
            async with s.post("https://www.virustotal.com/api/v3/urls",
                              headers=headers, data={"url": url}) as r:
                submit = await r.json()
            if "data" not in submit:
                return await message.edit(f"❌ {submit}")
            aid = submit["data"]["id"]
            async with s.get(f"https://www.virustotal.com/api/v3/analyses/{aid}",
                             headers=headers) as r:
                data = await r.json()
        stats = data["data"]["attributes"].get("stats", {})
        txt = (f"🔍 <b>Scan Result</b>\n"
               f"<b>URL:</b> <code>{url}</code>\n"
               f"✅ Harmless: {stats.get('harmless',0)}\n"
               f"⚠️ Suspicious: {stats.get('suspicious',0)}\n"
               f"🚨 Malicious: {stats.get('malicious',0)}")
        await message.edit(txt)