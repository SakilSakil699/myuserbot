"""
📊 Dashboard — System stats (Termux-safe)
"""

from helpers import cmd
import time
import platform
import os

START_TIME = time.time()


# ═══════════════════════════════════════════════════
#  SAFE HELPERS (Termux-compatible)
# ═══════════════════════════════════════════════════

def safe_cpu():
    """CPU % — /proc/stat may be blocked on Termux."""
    try:
        import psutil
        return f"{psutil.cpu_percent(interval=0.1)}%"
    except Exception:
        return "N/A"


def safe_ram():
    """RAM usage info."""
    try:
        import psutil
        ram = psutil.virtual_memory()
        used_mb = ram.used // 1024**2
        total_mb = ram.total // 1024**2
        return f"{ram.percent}% ({used_mb}/{total_mb} MB)"
    except Exception:
        return "N/A"


def safe_disk():
    """Disk usage info."""
    try:
        import psutil
        disk = psutil.disk_usage("/")
        used_gb = disk.used // 1024**3
        total_gb = disk.total // 1024**3
        return f"{disk.percent}% ({used_gb}/{total_gb} GB)"
    except Exception:
        return "N/A"


def safe_battery():
    """Battery status (Termux: requires termux-api)."""
    try:
        import psutil
        b = psutil.sensors_battery()
        if b:
            return f"{int(b.percent)}% {'⚡' if b.power_plugged else '🔋'}"
        return "N/A"
    except Exception:
        return "N/A"


def count_modules():
    """Count loaded modules."""
    try:
        return len([
            f for f in os.listdir("modules")
            if f.endswith(".py") and not f.startswith("_")
        ])
    except Exception:
        return "?"


def fmt_uptime(seconds):
    """Format uptime as Xh Ym Zs."""
    h, r = divmod(int(seconds), 3600)
    m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s"


# ═══════════════════════════════════════════════════
#  HANDLERS
# ═══════════════════════════════════════════════════

def register(app):

    @app.on_message(cmd("stats"))
    async def stats(client, message):
        try:
            uptime = fmt_uptime(time.time() - START_TIME)

            try:
                me = await client.get_me()
                uname = f"@{me.username}" if me.username else me.first_name
            except Exception:
                uname = "N/A"

            text = (
                f"📊 <b>Userbot Dashboard</b>\n\n"
                f"👤 <b>Account:</b> {uname}\n"
                f"⏱ <b>Uptime:</b> <code>{uptime}</code>\n\n"
                f"💻 <b>System</b>\n"
                f"<b>OS:</b> <code>{platform.system()} {platform.release()}</code>\n"
                f"<b>Python:</b> <code>{platform.python_version()}</code>\n"
                f"<b>CPU:</b> <code>{safe_cpu()}</code>\n"
                f"<b>RAM:</b> <code>{safe_ram()}</code>\n"
                f"<b>Disk:</b> <code>{safe_disk()}</code>\n"
                f"<b>Battery:</b> <code>{safe_battery()}</code>\n\n"
                f"📦 <b>Modules:</b> <code>{count_modules()}</code>"
            )

            await message.edit(text)

        except Exception as e:
            await message.edit(f"❌ <b>Stats error:</b>\n<code>{e}</code>")


    @app.on_message(cmd("sysinfo"))
    async def sysinfo(client, message):
        try:
            uptime = fmt_uptime(time.time() - START_TIME)

            text = (
                f"💻 <b>System Info</b>\n\n"
                f"<b>OS:</b> <code>{platform.system()} {platform.release()}</code>\n"
                f"<b>Python:</b> <code>{platform.python_version()}</code>\n"
                f"<b>CPU:</b> <code>{safe_cpu()}</code>\n"
                f"<b>RAM:</b> <code>{safe_ram()}</code>\n"
                f"<b>Disk:</b> <code>{safe_disk()}</code>\n"
                f"<b>Uptime:</b> <code>{uptime}</code>"
            )

            await message.edit(text)

        except Exception as e:
            await message.edit(f"❌ <b>Error:</b>\n<code>{e}</code>")
