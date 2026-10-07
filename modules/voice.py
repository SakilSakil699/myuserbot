from helpers import cmd
from gtts import gTTS
import os

def register(app):
    @app.on_message(cmd("tts"))
    async def tts(client, message):
        args = message.text.split(None, 2)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.tts [lang] text</code>")
        lang = "hi"
        text = args[1]
        if len(args) == 3 and len(args[1]) <= 3:
            lang, text = args[1], args[2]
        await message.edit("🔊 Generating...")
        try:
            tts = gTTS(text=text, lang=lang)
            path = f"tts_{message.id}.mp3"
            tts.save(path)
            await client.send_voice(message.chat.id, path)
            os.remove(path)
            await message.delete()
        except Exception as e:
            await message.edit(f"❌ {e}")