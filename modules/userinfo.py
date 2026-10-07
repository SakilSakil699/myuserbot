from pyrogram import filters
from config import PREFIX

def cmd(name):
    return filters.command(name, prefixes=PREFIX) & filters.me

def register(app):
    @app.on_message(cmd("info"))
    async def info(client, message):
        target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        chat = message.chat
        txt = (
            f"👤 <b>User Info</b>\n"
            f"<b>Name:</b> {target.first_name or ''} {target.last_name or ''}\n"
            f"<b>Username:</b> @{target.username or '—'}\n"
            f"<b>ID:</b> <code>{target.id}</code>\n"
            f"<b>Bot:</b> {target.is_bot}\n"
            f"<b>Premium:</b> {target.is_premium}\n\n"
            f"💬 <b>Chat Info</b>\n"
            f"<b>Title:</b> {chat.title or target.first_name}\n"
            f"<b>Type:</b> {chat.type.name}\n"
            f"<b>Chat ID:</b> <code>{chat.id}</code>\n"
        )
        try:
            full = await client.get_chat(target.id)
            if full.bio: txt += f"\n<b>Bio:</b> {full.bio}"
        except: pass
        await message.edit(txt)

    @app.on_message(cmd("sysinfo"))
    async def sysinfo(client, message):
        import psutil, platform, time
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        boot = time.time() - psutil.boot_time()
        txt = (
            f"💻 <b>System Info</b>\n"
            f"<b>OS:</b> {platform.system()} {platform.release()}\n"
            f"<b>Python:</b> {platform.python_version()}\n"
            f"<b>CPU:</b> {cpu}%\n"
            f"<b>RAM:</b> {ram.percent}% ({ram.used//1024**2}MB / {ram.total//1024**2}MB)\n"
            f"<b>Uptime:</b> {int(boot//3600)}h {int((boot%3600)//60)}m"
        )
        await message.edit(txt)