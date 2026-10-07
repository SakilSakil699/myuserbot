from helpers import cmd
import qrcode, os

def register(app):
    @app.on_message(cmd("qr"))
    async def qr(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.qr text_or_url</code>")
        data = args[1]
        await message.edit("🎨 Generating QR...")
        img = qrcode.make(data)
        path = f"qr_{message.id}.png"
        img.save(path)
        await client.send_photo(message.chat.id, path, caption=f"🔳 QR: {data[:50]}")
        os.remove(path)
        await message.delete()