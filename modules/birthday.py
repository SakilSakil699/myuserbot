from helpers import cmd
from database import DB
from datetime import datetime
import asyncio

db = DB("birthday")

def register(app):
    @app.on_message(cmd("bday"))
    async def bday(client, message):
        args = message.text.split()
        if len(args) < 2:
            return await message.edit(
                "🎂 <code>.bday add DD-MM Name</code>\n"
                "<code>.bday list</code>\n"
                "<code>.bday del Name</code>"
            )
        sub = args[1].lower()
        if sub == "add":
            if len(args) < 4: return await message.edit("⚠️ <code>.bday add DD-MM Name</code>")
            date, name = args[2], " ".join(args[3:])
            data = db.get("list", {})
            data[name] = date
            db.set("list", data)
            await message.edit(f"🎂 Added {name} → {date}")
        elif sub == "list":
            data = db.get("list", {})
            if not data: return await message.edit("📭 Empty.")
            txt = "🎂 <b>Birthdays:</b>\n"
            for name, date in sorted(data.items(), key=lambda x: x[1]):
                txt += f"\n• <b>{name}</b> — {date}"
            await message.edit(txt)
        elif sub == "del":
            if len(args) < 3: return
            data = db.get("list", {})
            name = " ".join(args[2:])
            if name in data:
                del data[name]; db.set("list", data)
                await message.edit(f"🗑 Deleted.")
            else:
                await message.edit("❌ Not found.")