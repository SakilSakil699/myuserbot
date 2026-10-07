from helpers import cmd
import asyncio

def register(app):
    @app.on_message(cmd("purge"))
    async def purge(client, message):
        if not message.reply_to_message:
            return await message.edit("⚠️ Reply to the FIRST message to delete from.")
        start_id = message.reply_to_message.id
        end_id = message.id
        await message.delete()
        ids = list(range(start_id, end_id + 1))
        for i in range(0, len(ids), 100):
            try:
                await client.delete_messages(message.chat.id, ids[i:i+100])
            except: pass
            await asyncio.sleep(1)
        msg = await client.send_message(message.chat.id, f"🧹 Purged {len(ids)} messages.")
        await asyncio.sleep(3)
        try: await msg.delete()
        except: pass