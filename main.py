import importlib
from pathlib import Path
from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, SESSION_STRING, BOT_NAME

app = Client("userbot", api_id=API_ID, api_hash=API_HASH,
             session_string=SESSION_STRING, parse_mode=ParseMode.HTML)

def load_all():
    for f in Path("modules").glob("*.py"):
        if f.name.startswith("_"): continue
        try:
            m = importlib.import_module(f"modules.{f.stem}")
            if hasattr(m, "register"):
                m.register(app)
                print(f"✅ {f.stem}")
        except Exception as e:
            print(f"❌ {f.stem}: {e}")

async def main():
    await app.start()
    me = await app.get_me()
    print(f"🔥 {BOT_NAME} as @{me.username or me.first_name}")
    load_all()
    await idle()

app.run(main())