"""
🔧 Utility Commands — ping, help, id, info
"""

from helpers import cmd
from config import BOT_PREFIX as PREFIX, BOT_NAME
import time

START_TIME = time.time()


def register(app):

    # ═══════════════════════════════════════════════
    #  .ping — Latency + Uptime
    # ═══════════════════════════════════════════════
    @app.on_message(cmd("ping"))
    async def ping(client, message):
        t1 = time.time()
        msg = await message.edit("🏓 Pong...")
        t2 = time.time()

        uptime = int(time.time() - START_TIME)
        h, r = divmod(uptime, 3600)
        m, s = divmod(r, 60)

        await msg.edit(
            f"🏓 <b>Pong!</b>\n\n"
            f"⚡ <b>Latency:</b> <code>{(t2 - t1) * 1000:.2f}ms</code>\n"
            f"⏱ <b>Uptime:</b> <code>{h}h {m}m {s}s</code>"
        )


    # ═══════════════════════════════════════════════
    #  .help — Commands List
    # ═══════════════════════════════════════════════
    @app.on_message(cmd("help"))
    async def help_cmd(client, message):
        p = PREFIX
        text = (
            f"🤖 <b>{BOT_NAME}</b>\n"
            f"<i>Prefix:</i> <code>{p}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"

            f"<b>🔧 Utility</b>\n"
            f"<code>{p}ping</code> — Latency check\n"
            f"<code>{p}id</code> — Chat/User ID\n"
            f"<code>{p}info</code> — User info\n"
            f"<code>{p}stats</code> — System stats\n"
            f"<code>{p}sysinfo</code> — OS/CPU/RAM\n\n"

            f"<b>😴 AFK</b>\n"
            f"<code>{p}afk [reason]</code>\n"
            f"<code>{p}unafk</code>\n\n"

            f"<b>📝 Notes</b>\n"
            f"<code>{p}save name text</code>\n"
            f"<code>{p}get name</code>\n"
            f"<code>{p}notes</code>\n"
            f"<code>{p}delnote name</code>\n\n"

            f"<b>🛡️ Security</b>\n"
            f"<code>{p}pmguard on/off</code>\n"
            f"<code>{p}antiflood on/off</code>\n"
            f"<code>{p}antifraud on/off</code>\n\n"

            f"<b>👑 Group</b>\n"
            f"<code>{p}ban</code> · <code>{p}kick</code> · <code>{p}mute</code>\n"
            f"<code>{p}warn</code> · <code>{p}pin</code> · <code>{p}tagall</code>\n"
            f"<code>{p}purge</code>\n\n"

            f"<b>🤖 AI</b>\n"
            f"<code>{p}ai question</code>\n"
            f"<code>{p}ask question</code>\n"
            f"<code>{p}sum 100</code>\n\n"

            f"<b>🎁 Automation</b>\n"
            f"<code>{p}schedule 5m text</code>\n"
            f"<code>{p}remind 1h text</code>\n"
            f"<code>{p}autodel 10</code>\n\n"

            f"<b>🎨 Fun</b>\n"
            f"<code>{p}weather Delhi</code>\n"
            f"<code>{p}tr hi Hello</code>\n"
            f"<code>{p}tts Hello</code>\n"
            f"<code>{p}qr text</code>\n"
            f"<code>{p}quote</code> — Reply to msg\n"
            f"<code>{p}short url</code>\n"
            f"<code>{p}price btc</code>\n\n"

            f"<b>📥 Download</b>\n"
            f"<code>{p}yt url</code> · <code>{p}ig url</code>\n\n"

            f"<b>🔐 Vault</b>\n"
            f"<code>{p}vault save name data</code>\n"
            f"<code>{p}vault get name</code>\n"
            f"<code>{p}vault list</code>\n\n"

            f"<b>👑 Admin</b>\n"
            f"<code>{p}restart</code> · <code>{p}logs</code> · <code>{p}update</code>\n"
        )
        await message.edit(text)


    # ═══════════════════════════════════════════════
    #  .id — Get User/Chat ID
    # ═══════════════════════════════════════════════
    @app.on_message(cmd("id"))
    async def getid(client, message):
        chat = message.chat
        text = f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>\n"

        target = None
        if message.reply_to_message and message.reply_to_message.from_user:
            target = message.reply_to_message.from_user
        elif message.from_user:
            target = message.from_user

        if target:
            text += (
                f"\n👤 <b>User:</b> {target.mention}\n"
                f"<b>ID:</b> <code>{target.id}</code>\n"
                f"<b>Username:</b> @{target.username or '—'}"
            )

        await message.edit(text)


    # ═══════════════════════════════════════════════
    #  .info — Detailed user info
    # ═══════════════════════════════════════════════
    @app.on_message(cmd("info"))
    async def info(client, message):
        target = None
        if message.reply_to_message and message.reply_to_message.from_user:
            target = message.reply_to_message.from_user
        else:
            target = message.from_user

        if not target:
            return await message.edit("❌ User not found.")

        text = (
            f"👤 <b>User Info</b>\n\n"
            f"<b>Name:</b> {target.first_name or ''} {target.last_name or ''}\n"
            f"<b>Username:</b> @{target.username or '—'}\n"
            f"<b>ID:</b> <code>{target.id}</code>\n"
            f"<b>Bot:</b> {'✅' if target.is_bot else '❌'}\n"
            f"<b>Premium:</b> {'✅' if getattr(target, 'is_premium', False) else '❌'}\n"
        )

        try:
            full = await client.get_chat(target.id)
            if full.bio:
                text += f"\n<b>Bio:</b> {full.bio}"
        except Exception:
            pass

        await message.edit(text)
