from pyrogram import filters
from config import BOT_PREFIX as PREFIX
import yt_dlp, os

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def register(app):
    @app.on_message(cmd("yt"))
    async def ytdl(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.yt url</code>")
        url = args[1]
        await message.edit("⬇️ Downloading...")
        opts = {
            "outtmpl": "dl_%(id)s.%(ext)s",
            "format": "best[filesize<50M]/best",
            "quiet": True,
            "noplaylist": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file = ydl.prepare_filename(info)
            await message.edit("📤 Uploading...")
            await client.send_video(message.chat.id, file, caption=f"🎬 {info.get('title','')}")
            os.remove(file)
            await message.delete()
        except Exception as e:
            await message.edit(f"❌ Failed: <code>{str(e)[:200]}</code>")
