from pyrogram import filters
from pyrogram.types import ChatPermissions
from helpers import cmd
import time

WARNS = {}

def register(app):
    @app.on_message(cmd("ban"))
    async def ban(client, message):
        if not message.reply_to_message:
            return await message.edit("⚠️ Reply to user.")
        u = message.reply_to_message.from_user
        try:
            await client.ban_chat_member(message.chat.id, u.id)
            await message.edit(f"🔨 Banned {u.mention}")
        except Exception as e:
            await message.edit(f"❌ {e}")

    @app.on_message(cmd("unban"))
    async def unban(client, message):
        if not message.reply_to_message: return
        u = message.reply_to_message.from_user
        try:
            await client.unban_chat_member(message.chat.id, u.id)
            await message.edit(f"✅ Unbanned {u.mention}")
        except Exception as e:
            await message.edit(f"❌ {e}")

    @app.on_message(cmd("kick"))
    async def kick(client, message):
        if not message.reply_to_message: return
        u = message.reply_to_message.from_user
        try:
            await client.ban_chat_member(message.chat.id, u.id)
            await client.unban_chat_member(message.chat.id, u.id)
            await message.edit(f"👢 Kicked {u.mention}")
        except Exception as e:
            await message.edit(f"❌ {e}")

    @app.on_message(cmd("mute"))
    async def mute(client, message):
        if not message.reply_to_message: return
        u = message.reply_to_message.from_user
        try:
            await client.restrict_chat_member(message.chat.id, u.id, ChatPermissions())
            await message.edit(f"🔇 Muted {u.mention}")
        except Exception as e:
            await message.edit(f"❌ {e}")

    @app.on_message(cmd("unmute"))
    async def unmute(client, message):
        if not message.reply_to_message: return
        u = message.reply_to_message.from_user
        perms = ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                can_send_other_messages=True, can_add_web_page_previews=True)
        try:
            await client.restrict_chat_member(message.chat.id, u.id, perms)
            await message.edit(f"🔊 Unmuted {u.mention}")
        except Exception as e:
            await message.edit(f"❌ {e}")

    @app.on_message(cmd("warn"))
    async def warn(client, message):
        if not message.reply_to_message: return
        u = message.reply_to_message.from_user
        key = f"{message.chat.id}_{u.id}"
        WARNS[key] = WARNS.get(key, 0) + 1
        if WARNS[key] >= 3:
            try: await client.ban_chat_member(message.chat.id, u.id)
            except: pass
            WARNS[key] = 0
            await message.edit(f"🔨 {u.mention} banned (3/3 warns)")
        else:
            await message.edit(f"⚠️ {u.mention} warned ({WARNS[key]}/3)")

    @app.on_message(cmd("pin"))
    async def pin(client, message):
        if not message.reply_to_message: return
        try:
            await message.reply_to_message.pin()
            await message.edit("📌 Pinned")
        except Exception as e:
            await message.edit(f"❌ {e}")

    @app.on_message(cmd("promote"))
    async def promote(client, message):
        if not message.reply_to_message: return
        u = message.reply_to_message.from_user
        try:
            await client.promote_chat_member(message.chat.id, u.id,
                can_delete_messages=True, can_restrict_members=True,
                can_pin_messages=True, can_invite_users=True)
            await message.edit(f"⬆️ Promoted {u.mention}")
        except Exception as e:
            await message.edit(f"❌ {e}")

    @app.on_message(cmd("demote"))
    async def demote(client, message):
        if not message.reply_to_message: return
        u = message.reply_to_message.from_user
        try:
            await client.promote_chat_member(message.chat.id, u.id)
            await message.edit(f"⬇️ Demoted {u.mention}")
        except Exception as e:
            await message.edit(f"❌ {e}")