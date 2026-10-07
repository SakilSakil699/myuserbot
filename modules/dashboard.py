from helpers import cmd
import psutil, time, platform, os

START = time.time()

def register(app):
    @app.on_message(cmd("stats"))
    async def stats(client, message):
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        up = int(time.time() - START)
        h, r = divmod(up, 3600); m, s = divmod(r, 60)
        try:
            me = await client.get_me()
            uname = f"@{me.username}" if me.username else me.first_name
        except: uname = "N/A"
        txt = (
            f"📊 <b>Userbot Dashboard</b>\n\n"
            f"👤 <b>Account:</b> {uname}\n"
            f"⏱ <b>Uptime:</b> <code>{h}h {m}m {s}s</code>\n\n"
            f"💻 <b>System</b>\n"
            f"OS: <code>{platform.system()}</code>\n"
            f"Python: <code>{platform.python_version()}</code>\n"
            f"CPU: <code>{cpu}%</code>\n"
            f"RAM: <code>{ram.percent}%</code> ({ram.used//1024**2}/{ram.total//1024**2} MB)\n"
            f"Disk: <code>{disk.percent}%</code>\n\n"
            f"📦 <b>Modules:</b> <code>{len(os.listdir('modules'))-1}</code>"
        )
        await message.edit(txt)