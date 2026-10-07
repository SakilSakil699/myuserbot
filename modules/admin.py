"""
👑 Admin commands
"""

import os
import sys
from pyrogram import filters
from helpers import cmd
from config import OWNER_ID


def register(app):

    # ─────────────────────────────────────
    #  /ping — check bot alive
    # ─────────────────────────────────────
    @app.on_message(cmd("ping"))
    async def ping(client, message):
        import time
        t = time.time()
        msg = await message.edit("🏓 Pong...")
        latency = (time.time() - t) * 1000
        await msg.edit(f"🏓 <b>Pong!</b>\n⚡ Latency: <code>{latency:.0f}ms</code>")


    # ─────────────────────────────────────
    #  /restart — restart bot
    # ─────────────────────────────────────
    @app.on_message(cmd("restart"))
    async def restart(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.edit("❌ Owner only!")
        await message.edit("♻️ Restarting...")
        os.execv(sys.executable, [sys.executable] + sys.argv)


    # ─────────────────────────────────────
    #  /update — pull from GitHub
    # ─────────────────────────────────────
    @app.on_message(cmd("update"))
    async def update_cmd(client, message):
        from core.updater import Updater
        await message.edit("🔄 Updating...")
        updater = Updater("https://github.com/SakilSakil699/myuserbot")
        ok, msg = updater.update()
        if ok:
            await message.edit("✅ Updated! Restarting...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            await message.edit(f"❌ Failed: <code>{msg}</code>")


    # ─────────────────────────────────────
    #  /logs — show recent logs
    # ─────────────────────────────────────
    @app.on_message(cmd("logs"))
    async def logs(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.edit("❌ Owner only!")
        try:
            with open("logs/userbot.log", "r", encoding="utf-8") as f:
                data = f.read()[-3000:]
            await message.edit(f"📜 <b>Logs:</b>\n<pre>{data}</pre>")
        except FileNotFoundError:
            await message.edit("❌ No logs found.")
