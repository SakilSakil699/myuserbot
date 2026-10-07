"""
🧪 TEST Rotation — 2 min interval
"""

import asyncio
from helpers import cmd
from config import OWNER_ID
from pyrogram.raw.functions.channels import UpdateUsername
from pyrogram.raw.functions.channels import GetChannels
from pyrogram.raw.types import InputChannel

CHANNEL_ID = -1002461966751
ROTATION_INTERVAL = 120  # 2 minutes

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

_app = None
_rotation_task = None
_current_index = 0


async def get_channel():
    res = await _app.invoke(
        GetChannels(id=[InputChannel(CHANNEL_ID, 0)])
    )
    return res.chats[0]


async def rotate_loop():
    global _current_index
    while True:
        try:
            new_username = USERNAME_POOL[_current_index % len(USERNAME_POOL)]
            _current_index += 1
            
            channel = await get_channel()
            await _app.invoke(
                UpdateUsername(channel=channel, username=new_username)
            )
            
            try:
                await _app.send_message(
                    OWNER_ID,
                    f"🧪 <b>TEST rotation</b>\nNew: @{new_username}"
                )
            except Exception:
                pass
        
        except Exception as e:
            try:
                await _app.send_message(
                    OWNER_ID,
                    f"❌ <b>Test failed:</b>\n<code>{e}</code>"
                )
            except Exception:
                pass
        
        await asyncio.sleep(ROTATION_INTERVAL)


def register(app):
    global _app
    _app = app
    
    @app.on_message(cmd("testrotate"))
    async def test_rotate(client, message):
        global _rotation_task, _current_index
        
        args = message.text.split()
        
        if len(args) > 1 and args[1].lower() == "off":
            if _rotation_task and not _rotation_task.done():
                _rotation_task.cancel()
                _rotation_task = None
            return await message.edit("🛑 <b>TEST OFF</b>")
        
        if _rotation_task and not _rotation_task.done():
            return await message.edit("⚠️ Test already running")
        
        _current_index = 0
        
        await message.edit(
            f"🧪 <b>TEST Rotation ON</b>\n\n"
            f"⏰ Interval: <code>2 minutes</code>\n"
            f"📝 Pool: <code>{len(USERNAME_POOL)}</code>"
        )
        
        _rotation_task = asyncio.create_task(rotate_loop())
