"""
🔄 Channel Username Auto-Rotator
Userbot ke liye — bot ke liye nahi
"""

import asyncio
from pyrogram import filters
from helpers import cmd
from config import OWNER_ID
from pyrogram.raw.functions.channels import UpdateUsername
from pyrogram.raw.functions.channels import GetChannels
from pyrogram.raw.types import InputChannel

# ═══ Config ═══
CHANNEL_ID = -1001234567890  # Apna channel ID daalo
ROTATION_INTERVAL = 3600  # 1 hour (seconds me) — 30 min se kam mat rakho
USERNAME_POOL = [
    "sakil11",
    "sakil13",
    "sakil14",
    "sakil15",
    "sakil16",
]

# State
_rotation_task = None
_current_index = 0


def register(app):

    @app.on_message(cmd("rotate"))
    async def toggle_rotate(client, message):
        global _rotation_task

        args = message.text.split()

        # Off
        if len(args) > 1 and args[1] == "off":
            if _rotation_task:
                _rotation_task.cancel()
                _rotation_task = None
            return await message.edit("🛑 Username rotation OFF")

        # On
        if _rotation_task:
            return await message.edit("⚠️ Rotation already ON")

        await message.edit(
            f"🔄 <b>Username Rotation ON</b>\n\n"
            f"Channel: <code>{CHANNEL_ID}</code>\n"
            f"Interval: <code>{ROTATION_INTERVAL}s</code>\n"
            f"Pool: <code>{len(USERNAME_POOL)}</code> usernames\n"
            f"<i>Next: {USERNAME_POOL[0]}</i>"
        )

        async def rotate_loop():
            global _current_index
            while True:
                try:
                    # Get channel
                    res = await app.invoke(
                        GetChannels(id=[InputChannel(CHANNEL_ID, 0)])
                    )
                    channel = res.chats[0]

                    # Get next username
                    new_username = USERNAME_POOL[_current_index % len(USERNAME_POOL)]
                    _current_index += 1

                    # Change username
                    await app.invoke(
                        UpdateUsername(
                            channel=channel,
                            username=new_username
                        )
                    )

                    # Notify owner
                    try:
                        await app.send_message(
                            OWNER_ID,
                            f"✅ <b>Username rotated!</b>\n\n"
                            f"New: <code>@{new_username}</code>"
                        )
                    except Exception:
                        pass

                except Exception as e:
                    try:
                        await app.send_message(
                            OWNER_ID,
                            f"❌ <b>Rotation failed:</b>\n<code>{e}</code>"
                        )
                    except Exception:
                        pass

                await asyncio.sleep(ROTATION_INTERVAL)

        _rotation_task = asyncio.create_task(rotate_loop())


    @app.on_message(cmd("setusername"))
    async def set_username_manual(client, message):
        """Manual username set — .setusername newname"""
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.setusername new_username</code>")

        new_username = args[1].strip()

        try:
            res = await app.invoke(
                GetChannels(id=[InputChannel(CHANNEL_ID, 0)])
            )
            channel = res.chats[0]

            await app.invoke(
                UpdateUsername(
                    channel=channel,
                    username=new_username
                )
            )

            await message.edit(f"✅ Username set: <code>@{new_username}</code>")

        except Exception as e:
            await message.edit(f"❌ Failed: <code>{e}</code>")
