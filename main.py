"""
🚀 Ultimate Advanced Telegram Userbot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Python 3.14 compatible • Termux ready
"""

# ═══════════════════════════════════════════════════
#  Python 3.14 Fix for Pyrogram
# ═══════════════════════════════════════════════════
import asyncio

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ═══════════════════════════════════════════════════
#  Quiet Pyrogram internal spam
# ═══════════════════════════════════════════════════
import logging

logging.getLogger("pyrogram").setLevel(logging.CRITICAL)
logging.getLogger("pyrogram.session").setLevel(logging.CRITICAL)
logging.getLogger("pyrogram.connection").setLevel(logging.CRITICAL)
logging.getLogger("pyrogram.dispatcher").setLevel(logging.CRITICAL)
logging.getLogger("pyrogram.methods").setLevel(logging.CRITICAL)

# ═══════════════════════════════════════════════════
#  Suppress "Peer id invalid" asyncio errors
# ═══════════════════════════════════════════════════
def _asyncio_exception_handler(loop, context):
    """Silently ignore Peer id invalid errors."""
    exc = context.get("exception")
    msg = str(exc) if exc else context.get("message", "")

    if "Peer id invalid" in msg or "ID not found" in msg:
        return  # Ignore silently

    # Show other errors normally
    loop.default_exception_handler(context)

# ═══════════════════════════════════════════════════
#  Standard imports
# ═══════════════════════════════════════════════════
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
    FloodWait,
)

# ═══════════════════════════════════════════════════
#  Load config
# ═══════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════
#  Global state
# ═══════════════════════════════════════════════════
START_TIME = time.time()
app: Client = None
_shutdown_event: asyncio.Event = None


def log(msg: str):
    """Timestamped logger."""
    t = time.strftime("%H:%M:%S")
    print(f"{t} | {msg}", flush=True)


# ═══════════════════════════════════════════════════
#  Session decryption
# ═══════════════════════════════════════════════════
def get_session_string() -> str:
    """Auto-detect encrypted session and decrypt."""
    if not SESSION_STRING:
        print("❌ SESSION_STRING missing in .env")
        sys.exit(1)

    # Fernet tokens start with 'gAAAAA'
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


# ═══════════════════════════════════════════════════
#  Client factory
# ═══════════════════════════════════════════════════
def create_client() -> Client:
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

    if PROXY and PROXY.get("hostname"):
        kwargs["proxy"] = PROXY
        log(f"🌐 Proxy: {PROXY['hostname']}:{PROXY['port']}")
    else:
        log("🌐 No proxy")

    return Client(**kwargs)


# ═══════════════════════════════════════════════════
#  Banner
# ═══════════════════════════════════════════════════
def print_banner():
    print(f"""
╔══════════════════════════════════════════════╗
║   🔥  {BOT_NAME.upper():<34} 🔥
║   Prefix: {PREFIX:<34} ║
║   Owner:  {str(OWNER_ID):<34} ║
╚══════════════════════════════════════════════╝
""")


# ═══════════════════════════════════════════════════
#  Plugin loader (with fallback)
# ═══════════════════════════════════════════════════
def load_plugins():
    """Load all modules from modules/ folder."""
    try:
        from core.plugin_manager import PluginManager
        pm = PluginManager(app, modules_dir="modules")
        pm.load_all()
        log(f"✅ Plugins: {len(pm.loaded)} loaded, {len(pm.failed)} failed")
        if pm.failed:
            for name, err in pm.failed.items():
                log(f"   ❌ {name}: {err}")
    except ImportError:
        # Fallback: simple loader
        log("⚠️  core/ missing — using simple loader")
        import importlib
        loaded = failed = 0
        for f in Path("modules").glob("*.py"):
            if f.name.startswith("_"):
                continue
            try:
                m = importlib.import_module(f"modules.{f.stem}")
                if hasattr(m, "register"):
                    m.register(app)
                    loaded += 1
                    log(f"✅ {f.stem}")
            except Exception as e:
                failed += 1
                log(f"❌ {f.stem}: {e}")
        log(f"✅ Plugins: {loaded} loaded, {failed} failed")


# ═══════════════════════════════════════════════════
#  Warm up peer cache
# ═══════════════════════════════════════════════════
async def warmup_peers():
    """Cache top 100 dialogs — kills 'Peer id invalid' errors."""
    log("🔥 Warming up peer cache...")
    try:
        count = 0
        async for _ in app.get_dialogs():
            count += 1
            if count >= 100:
                break
        log(f"✅ Cached {count} dialogs")
    except Exception as e:
        log(f"⚠️  Warm-up skipped: {e}")


# ═══════════════════════════════════════════════════
#  Startup
# ═══════════════════════════════════════════════════
async def startup():
    """Start client, verify session, load plugins."""
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

    # Warm peer cache
    await warmup_peers()

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
        uptime = int(time.time() - START_TIME)
        await app.send_message(
            OWNER_ID,
            f"🚀 <b>{BOT_NAME} online!</b>\n\n"
            f"👤 {me.mention}\n"
            f"🆔 <code>{me.id}</code>",
        )
        log("📨 Owner notified")
    except Exception as e:
        log(f"⚠️  Owner notify failed: {e}")


# ═══════════════════════════════════════════════════
#  Shutdown
# ═══════════════════════════════════════════════════
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
    log(f"📡 Signal received: {sig}")
    if _shutdown_event is not None:
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(shutdown(sig))
        except Exception:
            pass


# ═══════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════
async def main():
    global app, _shutdown_event

    _shutdown_event = asyncio.Event()

    # Set asyncio exception handler (suppresses Peer id errors)
    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(_asyncio_exception_handler)
    except Exception:
        pass

    # Register signal handlers
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except Exception:
        pass

    # Build client
    app = create_client()

    # Startup
    await startup()

    # Keep running until shutdown
    try:
        await _shutdown_event.wait()
    except asyncio.CancelledError:
        await shutdown()


# ═══════════════════════════════════════════════════
#  Crash recovery wrapper
# ═══════════════════════════════════════════════════
def run_with_recovery():
    """Auto-restart on crash (max 5 retries)."""
    max_retries = 5
    delay = 10

    for attempt in range(1, max_retries + 1):
        try:
            asyncio.run(main())
            break  # Clean exit
        except KeyboardInterrupt:
            log("⌨️  Interrupted by user")
            break
        except Exception as e:
            log(f"💥 Crash ({attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                log(f"⏳ Restart in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                print("❌ Max retries reached. Exiting.")
                sys.exit(1)


# ═══════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    try:
        run_with_recovery()
    except KeyboardInterrupt:
        log("👋 Interrupted.")
