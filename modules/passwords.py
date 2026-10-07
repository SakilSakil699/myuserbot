from helpers import cmd
from database import DB
from cryptography.fernet import Fernet
import base64, hashlib, os

db = DB("vault")
MASTER = os.getenv("VAULT_KEY", "change-this-key")

def get_fernet():
    key = base64.urlsafe_b64encode(hashlib.sha256(MASTER.encode()).digest())
    return Fernet(key)

def register(app):
    @app.on_message(cmd("vault"))
    async def vault(client, message):
        args = message.text.split(None, 3)
        if len(args) < 2:
            return await message.edit(
                "🔐 <b>Vault</b>\n"
                "<code>.vault save name user|pass</code>\n"
                "<code>.vault get name</code>\n"
                "<code>.vault list</code>\n"
                "<code>.vault del name</code>"
            )
        sub = args[1].lower()
        f = get_fernet()
        if sub == "save":
            if len(args) < 4: return await message.edit("⚠️ <code>.vault save name user|pass</code>")
            name, data = args[2], args[3]
            enc = f.encrypt(data.encode()).decode()
            db.set(name, enc)
            await message.edit(f"🔐 Saved: <code>{name}</code>")
        elif sub == "get":
            if len(args) < 3: return
            name = args[2]
            enc = db.get(name)
            if not enc: return await message.edit("❌ Not found.")
            dec = f.decrypt(enc.encode()).decode()
            await message.edit(f"🔓 <b>{name}:</b>\n<code>{dec}</code>")
        elif sub == "list":
            keys = list(db.all().keys())
            txt = "🔐 <b>Vault:</b>\n" + "\n".join(f"• <code>{k}</code>" for k in keys) if keys else "📭 Empty."
            await message.edit(txt)
        elif sub == "del":
            if len(args) < 3: return
            db.delete(args[2])
            await message.edit(f"🗑 Deleted.")