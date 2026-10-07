"""
📊 Dashboard — System stats (Termux-compatible)
"""

from helpers import cmd
import time
import platform
import os

START_TIME = time.time()


def safe_cpu():
    """Get CPU % safely — returns N/A if Termux blocks /proc/stat."""
    try:
        import psutil
        return f"{psutil.cpu_percent(interval=0.1)}%"
    except (PermissionError, FileNotFoundError, Exception):
        return "N/A (Termux)"


def safe_ram():
    """Get RAM info safely."""
    try:
        import psutil
        ram = psutil.virtual_memory()
        return f"{ram.percent}% ({ram.used // 1024**2}MB / {ram.total // 1024**2}MB)"
    except Exception:
        return "N/A"


def safe_disk():
    """Get disk info safely."""
    try:
        import psutil
        disk = psutil.disk_usage("/")
        return f"{disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)"
    except Exception:
        return "N/A"


def register(app):

    @app.on_message(cmd("stats"))
    async def stats(client, message):
        try:
            uptime = int(time.time() - START_TIME)
            h, r = divmod(uptime, 3600)
            m, s = divmod(r, 60)

            try:
                me = await client.get_me()
                uname = f"@{me.username}" if me.username else me.first_name
            except Exception:
                uname = "N/A"

            # Count modules safely
            try:
                mod_count = len([f for f in os.listdir("modules") if f.endswith(".py") and not f.startswith("_")])
            except Exception:
                mod_count = "?"

            text = (
                f"📊 <b>Userbot Dashboard</b>\n\n"
                f"👤 <b>Account:</b> {uname}\n"
                f"⏱ <b>Uptime:</b> <code>{h}h {m}m {s}s</code>\n\n"
                f"💻 <b>System</b>\n"
                f"OS: <code>{platform.system()}</code>\n"
                f"Python: <code>{platform.python_version()}</code>\n"
                f"CPU: <code>{safe_cpu()}</code>\n"
                f"RAM: <code>{safe_ram()}</code>\n"
                f"Disk: <code>{safe_disk()}</code>\n\n"
                f"📦 <b>Modules:</b> <code>{mod_count}</code>"
            )

            await message.edit(text)

        except Exception as e:
            await message.edit(f"❌ <b>Stats error:</b>\n<code>{e}</code>")


    @app.on_message(cmd("sysinfo"))
    async def sysinfo(client, message):
        """Simpler sysinfo — no psutil crash."""
        uptime = int(time.time() - START_TIME)
        h, r = divmod(uptime, 3600)
        m, s = divmod(r, 60)

        text = (
            f"💻 <b>System Info</b>\n"
            f"OS: <code>{platform.system()} {platform.release()}</code>\n"
            f"Python: <code>{platform.python_version()}</code>\n"
            f"CPU: <code>{safe_cpu()}</code>\n"
            f"RAM: <code>{safe_ram()}</code>\n"
            f"Uptime: <code>{h}h {m}m {s}s</code>"
        )
        await message.edit(text)
