from helpers import cmd
import os, re, subprocess

def register(app):
    @app.on_message(cmd("ig"))
    async def igdl(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.ig instagram_url</code>")
        url = args[1]
        await message.edit("⬇️ Downloading...")
        try:
            subprocess.run([
                "instaloader", "--no-captions", "--no-metadata",
                "--dirname-pattern", "ig_dl",
                "--", url
            ], check=True, capture_output=True, timeout=120)
            # Find the file
            path = None
            for root, _, files in os.walk("ig_dl"):
                for f in files:
                    if f.endswith((".mp4", ".jpg")):
                        path = os.path.join(root, f); break
                if path: break
            if not path:
                return await message.edit("❌ Download failed.")
            if path.endswith(".mp4"):
                await client.send_video(message.chat.id, path, caption="📥 Instagram")
            else:
                await client.send_photo(message.chat.id, path, caption="📥 Instagram")
            os.remove(path)
            await message.delete()
        except Exception as e:
            await message.edit(f"❌ {str(e)[:200]}")