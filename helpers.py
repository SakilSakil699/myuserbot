import time

def cmd(name, prefixes=None):
    """Filter shortcut"""
    from config import BOT_PREFIX as PREFIX
    from pyrogram import filters
    p = prefixes or PREFIX
    return filters.command(name, prefixes=p) & filters.me

def humanize(sec):
    h, r = divmod(int(sec), 3600)
    m, s = divmod(r, 60)
    if h: return f"{h}h {m}m {s}s"
    if m: return f"{m}m {s}s"
    return f"{s}s"

def uptime_bar(start):
    return humanize(time.time() - start)
