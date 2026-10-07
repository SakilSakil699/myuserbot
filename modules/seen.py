from pyrogram import filters
from helpers import cmd
from database import DB
import time

db = DB("seen")

def register(app):
    @app.on_message(filters.private & ~filters.me, group=60)
    async def track(client, message):
        if not message.from_user: return
        uid = message.from_user.id
        db.set(uid, {"name": message.from_user.first_name, "time": time.time(),
                     "msg": (message.text or "[media]")[:100]})

    @app.on_message(cmd("seen"))
    async def get_seen(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2:
            # Show all
            all_data = db.all()
            if not all_data: return await message.edit("📭 No data.")
            txt = "👁 <b>Recently seen:</b>\n"
            for uid, d in sorted(all_data.items(), key=lambda x: -x[1]["time"])[:10]:
                mins = int((time.time() - d["time"]) / 60)
                txt += f"\n• <b>{d['name']}</b> ({mins}m ago)"
            return await message.edit(txt)
        try: uid = int(args[1])
        except: return
        d = db.get(uid)
        if not d: return await message.edit("❌ No data.")
        await message.edit(f"👁 <b>{d['name']}</b>\nLast: {d['msg']}")