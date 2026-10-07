from helpers import cmd
import os

def register(app):
    @app.on_message(cmd("setpfp"))
    async def setpfp(client, message):
        target = message.reply_to_message or message
        if not target.photo:
            return await message.edit("⚠️ Reply to a photo.")
        path = await client.download_media(target)
        try:
            await client.set_profile_photo(photo=path)
            await message.edit("✅ Profile photo updated!")
        except Exception as e:
            await message.edit(f"❌ {e}")
        finally:
            if os.path.exists(path): os.remove(path)

    @app.on_message(cmd("setname"))
    async def setname(client, message):
        args = message.text.split(None, 2)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.setname First Last</code>")
        first = args[1]
        last = args[2] if len(args) > 2 else ""
        try:
            await client.update_profile(first_name=first, last_name=last)
            await message.edit(f"✅ Name: {first} {last}")
        except Exception as e:
            await message.edit(f"❌ {e}")

    @app.on_message(cmd("setbio"))
    async def setbio(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2: return await message.edit("⚠️ <code>.setbio text</code>")
        try:
            await client.update_profile(bio=args[1])
            await message.edit("✅ Bio updated!")
        except Exception as e:
            await message.edit(f"❌ {e}")