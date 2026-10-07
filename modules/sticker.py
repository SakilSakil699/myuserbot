from pyrogram import filters
from config import BOT_PREFIX as PREFIX
from PIL import Image
import os

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def register(app):
    @app.on_message(cmd("kang"))
    async def kang(client, message):
        target = message.reply_to_message or message
        if not target.photo and not target.sticker:
            return await message.edit("⚠️ Reply to a photo/sticker.")
        await message.edit("🎨 Creating sticker...")
        path = await client.download_media(target)
        try:
            img = Image.open(path).convert("RGBA")
            # Resize to 512x512 while keeping aspect
            img.thumbnail((512, 512))
            canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            canvas.paste(img, ((512 - img.width)//2, (512 - img.height)//2), img)
            out = f"sticker_{message.id}.webp"
            canvas.save(out, "WEBP")
            await client.send_sticker(message.chat.id, out)
            await message.delete()
            os.remove(path); os.remove(out)
        except Exception as e:
            await message.edit(f"❌ Error: <code>{e}</code>")
