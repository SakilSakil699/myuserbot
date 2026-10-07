from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import BOT_PREFIX as PREFIX, OWNER_ID
import json, os, time

PM_FILE = "pm_permit.json"

def load():
    if os.path.exists(PM_FILE):
        with open(PM_FILE) as f: return json.load(f)
    return {"enabled": False, "approved": [], "pending": {}}

def save(d):
    with open(PM_FILE, "w") as f: json.dump(d, f)

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def register(app):
    data = load()

    @app.on_message(cmd("pmguard"))
    async def toggle(client, message):
        args = message.text.split()
        if len(args) < 2 or args[1] not in ["on", "off"]:
            return await message.edit("⚠️ Usage: <code>.pmguard on/off</code>")
        data["enabled"] = args[1] == "on"
        save(data)
        await message.edit(f"🛡 <b>PM Guard:</b> {'ON' if data['enabled'] else 'OFF'}")

    @app.on_message(cmd("approve"))
    async def approve(client, message):
        if not message.reply_to_message:
            return await message.edit("⚠️ Reply to a user's message.")
        uid = message.reply_to_message.from_user.id
        if uid not in data["approved"]:
            data["approved"].append(uid)
            save(data)
        await message.edit(f"✅ <b>Approved:</b> <code>{uid}</code>")

    @app.on_message(filters.private & ~filters.me, group=5)
    async def pm_handler(client, message):
        if not data["enabled"]:
            return
        uid = message.from_user.id
        if uid == OWNER_ID or uid in data["approved"]:
            return
        # Rate limit: 1 warning per 5 min
        now = time.time()
        last = data["pending"].get(str(uid), 0)
        if now - last < 300:
            return
        data["pending"][str(uid)] = now
        save(data)

        me = await client.get_me()
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ I'm Human", callback_data=f"pmverify_{uid}")
        ]])
        await message.reply(
            f"👋 <b>Hi {message.from_user.first_name}!</b>\n\n"
            f"Ye <b>{me.first_name}</b> ka personal account hai.\n"
            f"Pehle verify karo, fir baat kar sakte ho.\n\n"
            f"⚠️ 3 warnings ke baad <b>block</b> ho jaoge.",
            reply_markup=buttons
        )

    @app.on_callback_query(filters.regex(r"^pmverify_"))
    async def verify_cb(client, cq: CallbackQuery):
        uid = int(cq.data.split("_")[1])
        if cq.from_user.id != uid:
            return await cq.answer("Ye button tumhare liye nahi hai!", show_alert=True)
        await cq.message.edit(
            f"✅ <b>Verified!</b>\nAb tum message bhej sakte ho. Reply aane me time lag sakta hai."
        )
        # Notify owner
        try:
            await client.send_message(OWNER_ID,
                f"🔔 <b>PM Request</b>\nUser: {cq.from_user.mention}\nID: <code>{uid}</code>")
        except: pass
