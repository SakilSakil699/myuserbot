from helpers import cmd
from PIL import Image, ImageDraw, ImageFont
import os, textwrap

def register(app):
    @app.on_message(cmd("quote"))
    async def quote(client, message):
        if not message.reply_to_message or not message.reply_to_message.text:
            return await message.edit("⚠️ Reply to a text message.")
        src = message.reply_to_message
        await message.edit("🎨 Making quote image...")

        # Get profile photo
        try:
            pfp_path = await client.download_media(src.from_user.photo.big_file_id if src.from_user.photo else None)
        except: pfp_path = None

        W, H = 800, 400
        bg = Image.new("RGB", (W, H), (24, 24, 32))
        draw = ImageDraw.Draw(bg)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = small = ImageFont.load_default()

        # Wrap text
        lines = textwrap.wrap(src.text, width=40)[:8]
        y = 80
        for line in lines:
            draw.text((80, y), line, fill="white", font=font)
            y += 40

        draw.text((80, H - 60), f"— {src.from_user.first_name}", fill=(180, 180, 200), font=small)

        # Paste pfp if available
        if pfp_path and os.path.exists(pfp_path):
            try:
                pfp = Image.open(pfp_path).convert("RGB").resize((100, 100))
                mask = Image.new("L", (100, 100), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, 100, 100), fill=255)
                bg.paste(pfp, (W - 140, H - 140), mask)
            except: pass

        out = f"quote_{message.id}.png"
        bg.save(out)
        await client.send_photo(message.chat.id, out)
        os.remove(out)
        if pfp_path and os.path.exists(pfp_path): os.remove(pfp_path)
        await message.delete()