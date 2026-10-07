"""
🧪 TEST Username Rotation — 2 minute interval
Channel: Friends (-1002461966751)
"""

import asyncio
from pyrogram.raw.functions.channels import UpdateUsername
from helpers import cmd
from config import OWNER_ID


# ═══════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════

CHANNEL_ID = -1002461966751
ROTATION_INTERVAL = 120  # 2 minutes (test)

USERNAME_POOL = [
    "sakilAnowar1",
    "sakilAnowar2",
    "sakilAnowar3",
    "sakilAnowar4",
    "sakilAnowar5",
    "sakilAnowar6",
    "sakilAnowar7",
    "sakilAnowar8",
    "sakilAnowar9",
    "sakilAnowar10",
]


# ═══════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════

_app = None
_rotation_task = None
_current_index = 0


# ═══════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════

async def get_channel_peer():
    """Resolve channel peer safely."""
    chat = await _app.get_chat(CHANNEL_ID)
    return await _app.resolve_peer(chat.id)


async def change_username(new_username):
    """Change channel username via raw API."""
    peer = await get_channel_peer()
    await _app.invoke(
        UpdateUsername(channel=peer, username=new_username)
    )
    return new_username


async def get_current_username():
    """Get current channel username."""
    chat = await _app.get_chat(CHANNEL_ID)
    return chat.username or "—"


# ═══════════════════════════════════════════════════
#  ROTATION LOOP
# ═══════════════════════════════════════════════════

async def rotate_loop():
    """Main rotation loop."""
    global _current_index

    while True:
        try:
            new_username = USERNAME_POOL[_current_index % len(USERNAME_POOL)]
            _current_index += 1

            # Skip if already current
            current = await get_current_username()
            if current == new_username:
                # Move to next
                new_username = USERNAME_POOL[_current_index % len(USERNAME_POOL)]
                _current_index += 1

            await change_username(new_username)

            # Success notify
            try:
                await _app.send_message(
                    OWNER_ID,
                    f"🧪 <b>TEST Rotation</b>\n\n"
                    f"✅ New: @{new_username}\n"
                    f"⏰ Next in {ROTATION_INTERVAL // 60} min"
                )
            except Exception:
                pass

        except Exception as e:
            try:
                await _app.send_message(
                    OWNER_ID,
                    f"❌ <b>Test rotation failed:</b>\n<code>{e}</code>"
                )
            except Exception:
                pass

        await asyncio.sleep(ROTATION_INTERVAL)


# ═══════════════════════════════════════════════════
#  HANDLERS
# ═══════════════════════════════════════════════════

def register(app):
    global _app
    _app = app

    @app.on_message(cmd("testrotate"))
    async def test_rotate(client, message):
        global _rotation_task, _current_index

        args = message.text.split()

        # ── OFF ──
        if len(args) > 1 and args[1].lower() == "off":
            if _rotation_task and not _rotation_task.done():
                _rotation_task.cancel()
                _rotation_task = None
            return await message.edit("🛑 <b>TEST Rotation OFF</b>")

        # ── Already running ──
        if _rotation_task and not _rotation_task.done():
            return await message.edit("⚠️ Test already running")

        # ── Reset ──
        _current_index = 0

        # Current username
        try:
            current = await get_current_username()
        except Exception:
            current = "—"

        await message.edit(
            f"🧪 <b>TEST Rotation ON</b>\n\n"
            f"🆔 Channel: <code>{CHANNEL_ID}</code>\n"
            f"📛 Current: @{current}\n"
            f"⏰ Interval: <code>2 min</code>\n"
            f"📝 Pool: <code>{len(USERNAME_POOL)}</code> usernames\n\n"
            f"<i>First rotation in 2 minutes...</i>"
        )

        _rotation_task = asyncio.create_task(rotate_loop())


    @app.on_message(cmd("testcurrent"))
    async def test_current(client, message):
        """Show current channel username."""
        try:
            current = await get_current_username()
            await message.edit(f"📛 <b>Current:</b> @{current}")
        except Exception as e:
            await message.edit(f"❌ <code>{e}</code>")


    @app.on_message(cmd("testonce"))
    async def test_once(client, message):
        """Rotate once immediately — for quick testing."""
        global _current_index

        try:
            new_username = USERNAME_POOL[_current_index % len(USERNAME_POOL)]
            _current_index += 1

            await change_username(new_username)
            await message.edit(f"✅ <b>Rotated once:</b> @{new_username}")
        except Exception as e:
            await message.edit(f"❌ <code>{e}</code>")
