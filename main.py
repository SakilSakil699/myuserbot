"""
🚀 Ultimate Advanced Telegram Userbot
Python 3.14 compatible
"""

import asyncio

# ═══ Python 3.14 Fix for Pyrogram ═══
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# ═══════════════════════════════════

import os
import sys
import signal
import time
from pathlib import Path

from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    AuthKeyUnregistered,
    UserDeactivated,
    SessionRevoked,
)

# ═══ Load Config ═══
try:
    from config import (
        API_ID,
        API_HASH,
        SESSION_STRING,
        OWNER_ID,
        BOT_NAME,
        BOT_PREFIX as PREFIX,
        PROXY,
        DASHBOARD_ENABLED,
        DASHBOARD_PORT,
    )
except ImportError as e:
    print(f"❌ config.py load failed: {e}")
    sys.exit(1)

# ═══ Global State ═══
START_TIME = time.time()
app = None
_shutdown_event = None


def log(msg):
    """Simple logger."""
    t = time.strftime("%H:%M:%S")
    print(f"{t} | {msg}")


def get_session_string():
    """Check if session is encrypted or plain."""
    if not SESSION_STRING:
        print("❌ SESSION_STRING missing in .env")
        sys.exit(1)

    # Encrypted (Fernet) tokens start with 'gAAAAA'
    if SESSION_STRING.startswith("gAAAAA"):
        try:
            from core.session_vault import SessionVault
            decrypted = SessionVault().unlock(SESSION_STRING)
            log("🔐 Encrypted session unlocked")
            return decrypted
        except Exception as e:
            print(f"❌ Session unlock failed: {e}")
            sys.exit(1)

    log("⚠️  Session is PLAIN (not encrypted)")
    return SESSION_STRING


def create_client():
    """Build Pyrogram client."""
    kwargs = {
        "name": "userbot",
        "api_id": API_ID,
        "api_hash": API_HASH,
        "session_string": get_session_string(),
        "parse_mode": ParseMode.HTML,
        "workers": 20,
        "sleep_threshold": 60,
    }

    # Add proxy if configured
    if PROXY and PROXY.get("hostname"):
        kwargs["proxy"] = PROXY
        log(f"🌐 Proxy: {PROXY['hostname']}:{PROXY['port']}")
    else:
        log("🌐 No proxy")

    return Client(**kwargs)


def print_banner():
    print(f"""
╔══════════════════════════════════════════════╗
║   🔥  {BOT_NAME.upper():<35} 🔥
║   Prefix: {PREFIX:<34} ║
║   Owner:  {str(OWNER_ID):<34} ║
╚══════════════════════════════════════════════╝
""")


def load_plugins():
    """Load all modules from modules/ folder."""
    try:
        from core.plugin_manager import PluginManager
        pm = PluginManager(app, modules_dir="modules")
        pm.load_all()
        log(f"✅ Plugins: {len(pm.loaded)} loaded, {len(pm.failed)} failed")
    except ImportError:
        # Fallback: manual load if core/ missing
        log("⚠️ core/ missing — using simple loader")
        import importlib
        for f in Path("modules").glob("*.py"):
            if f.name.startswith("_"):
                continue
            try:
                m = importlib.import_module(f"modules.{f.stem}")
                if hasattr(m, "register"):
                    m.register(app)
                    log(f"✅ {f.stem}")
            except Exception as e:
                log(f"❌ {f.stem}: {e}")


async def startup():
    """Start client, load plugins."""
    print_banner()
    log("🚀 Starting userbot...")

    # Start Pyrogram
    try:
        await app.start()
    except AuthKeyUnregistered:
        print("❌ Session revoked! Generate new SESSION_STRING.")
        sys.exit(1)
    except UserDeactivated:
        print("❌ Account deactivated!")
        sys.exit(1)
    except SessionRevoked:
        print("❌ Session revoked from Telegram!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)

    # Get account info
    me = await app.get_me()
    log(f"✅ Logged in as: {me.first_name} (@{me.username or 'no-username'})")
    log(f"   User ID: {me.id}")

    if me.id != OWNER_ID:
        log(f"⚠️  OWNER_ID mismatch: env={OWNER_ID} actual={me.id}")

    # Dashboard (optional)
    if DASHBOARD_ENABLED:
        try:
            from core.web_dashboard import start_dashboard
            start_dashboard(port=DASHBOARD_PORT)
            log(f"📊 Dashboard: http://0.0.0.0:{DASHBOARD_PORT}")
        except Exception as e:
            log(f"⚠️  Dashboard skipped: {e}")

    # Load plugins
    log("📦 Loading plugins...")
    load_plugins()

    # Notify owner
    try:
        await app.send_message(
            OWNER_ID,
            f"🚀 <b>{BOT_NAME} online!</b>\n\n"
            f"👤 {me.mention}\n"
            f"🆔 <code>{me.id}</code>"
        )
    except Exception as e:
        log(f"⚠️  Owner notify failed: {e}")


async def shutdown(sig=None):
    """Graceful shutdown."""
    global _shutdown_event
    if _shutdown_event is None or _shutdown_event.is_set():
        return
    _shutdown_event.set()

    log(f"🛑 Shutting down (signal={sig})...")
    try:
        if app and app.is_connected:
            try:
                await app.send_message(OWNER_ID, "🔴 <b>Userbot stopped.</b>")
            except Exception:
                pass
            await app.stop()
            log("✅ Client stopped")
    except Exception as e:
        log(f"❌ Shutdown error: {e}")
    log("👋 Bye!")


def signal_handler(sig, frame):
    """Sync signal → async shutdown."""
    log(f"📡 Signal: {sig}")
    if _shutdown_event is not None:
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(shutdown(sig))
        except Exception:
            pass


async def main():
    global app, _shutdown_event

    _shutdown_event = asyncio.Event()

    # Signal handlers
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except Exception:
        pass

    # Build client
    app = create_client()

    # Startup
    await startup()

    # Keep running
    try:
        await _shutdown_event.wait()
    except asyncio.CancelledError:
        await shutdown()


def run_with_recovery():
    """Auto-restart on crash (max 5 times)."""
    max_retries = 5
    delay = 10

    for attempt in range(1, max_retries + 1):
        try:
            asyncio.run(main())
            break
        except KeyboardInterrupt:
            log("⌨️  Interrupted")
            break
        except Exception as e:
            log(f"💥 Crash ({attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                log(f"⏳ Restart in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                print("❌ Max retries. Exiting.")
                sys.exit(1)


if __name__ == "__main__":
    # Ensure folders
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    run_with_recovery()
