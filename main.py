"""
╔══════════════════════════════════════════════════════════════╗
║          🚀 ULTIMATE ADVANCED TELEGRAM USERBOT 🚀            ║
║                                                              ║
║  Features:                                                   ║
║   • Self-Healing Plugin Manager                              ║
║   • Locked Session Protocol                                  ║
║   • Agentic AI with Tools                                    ║
║   • Web Dashboard                                            ║
║   • Self-Updating System                                     ║
║   • SOCKS5 Proxy Support                                     ║
║   • Graceful Shutdown                                        ║
║   • Crash Recovery                                           ║
╚══════════════════════════════════════════════════════════════╝
"""

import asyncio
import os
import sys
import signal
import time
import logging
from pathlib import Path

from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from pyrogram.errors import (
    AuthKeyUnregistered,
    UserDeactivated,
    SessionRevoked,
    FloodWait,
)

# ═══════════════════════════════════════════════════════════════
#  IMPORT CORE MODULES
# ═══════════════════════════════════════════════════════════════
from core.logger import setup_logger
from core.session_vault import SessionVault
from core.plugin_manager import PluginManager
from core.web_dashboard import start_dashboard

# ═══════════════════════════════════════════════════════════════
#  SETUP LOGGING
# ═══════════════════════════════════════════════════════════════
logger = setup_logger()

# ═══════════════════════════════════════════════════════════════
#  LOAD CONFIG
# ═══════════════════════════════════════════════════════════════
try:
    from config import (
        API_ID,
        API_HASH,
        SESSION_STRING,
        OWNER_ID,
        BOT_NAME,
        PREFIX,
        PROXY,
        DASHBOARD_PORT,
        DASHBOARD_ENABLED,
    )
except ImportError as e:
    logger.critical(f"❌ config.py load failed: {e}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
#  GLOBAL STATE
# ═══════════════════════════════════════════════════════════════
START_TIME = time.time()
app: Client = None
plugin_manager: PluginManager = None
_shutdown_event = asyncio.Event()

# ═══════════════════════════════════════════════════════════════
#  DECRYPT SESSION (Locked Session Protocol)
# ═══════════════════════════════════════════════════════════════
def get_session_string():
    """Auto-detect if session is encrypted or plain."""
    if not SESSION_STRING:
        logger.critical("❌ SESSION_STRING missing in .env")
        sys.exit(1)

    # Encrypted Fernet tokens start with 'gAAAAA'
    if SESSION_STRING.startswith("gAAAAA"):
        try:
            vault = SessionVault()
            decrypted = vault.unlock(SESSION_STRING)
            logger.info("🔐 Encrypted session unlocked successfully")
            return decrypted
        except Exception as e:
            logger.critical(f"❌ Session unlock failed: {e}")
            sys.exit(1)

    logger.warning("⚠️  Session is PLAIN (not encrypted). Consider using SessionVault.")
    return SESSION_STRING

# ═══════════════════════════════════════════════════════════════
#  CREATE PYROGRAM CLIENT
# ═══════════════════════════════════════════════════════════════
def create_client():
    """Build Pyrogram client with proxy if configured."""
    kwargs = {
        "name": "userbot",
        "api_id": API_ID,
        "api_hash": API_HASH,
        "session_string": get_session_string(),
        "parse_mode": ParseMode.HTML,
        "workers": 20,               # Concurrent workers
        "sleep_threshold": 60,        # Auto-handle FloodWait < 60s
        "no_updates": False,
        "in_memory": False,
    }

    # Add proxy if set
    if PROXY and PROXY.get("hostname"):
        kwargs["proxy"] = PROXY
        logger.info(f"🌐 Proxy enabled: {PROXY['hostname']}:{PROXY['port']}")
    else:
        logger.info("🌐 Running without proxy")

    return Client(**kwargs)

# ═══════════════════════════════════════════════════════════════
#  BANNER
# ═══════════════════════════════════════════════════════════════
def print_banner():
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🔥  {BOT_NAME.upper():^50}  🔥
║                                                              ║
║   Version    : 3.0 Ultimate                                  ║
║   Prefix     : {PREFIX:<45}║
║   Owner ID   : {str(OWNER_ID):<45}║
║   Dashboard  : {'ENABLED @ :' + str(DASHBOARD_PORT) if DASHBOARD_ENABLED else 'DISABLED':<45}║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

# ═══════════════════════════════════════════════════════════════
#  STARTUP SEQUENCE
# ═══════════════════════════════════════════════════════════════
async def startup():
    """Start client, verify session, load plugins."""
    global plugin_manager

    print_banner()
    logger.info("🚀 Starting userbot...")

    # Start Pyrogram
    try:
        await app.start()
    except AuthKeyUnregistered:
        logger.critical("❌ Session revoked! Generate new SESSION_STRING.")
        sys.exit(1)
    except UserDeactivated:
        logger.critical("❌ Account deactivated!")
        sys.exit(1)
    except SessionRevoked:
        logger.critical("❌ Session revoked from Telegram!")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"❌ Failed to start: {e}")
        sys.exit(1)

    # Get account info
    me = await app.get_me()
    logger.info(f"✅ Logged in as: {me.first_name} (@{me.username or 'no-username'})")
    logger.info(f"   User ID: {me.id}")

    # Verify owner
    if me.id != OWNER_ID:
        logger.warning(f"⚠️  OWNER_ID ({OWNER_ID}) != logged-in ({me.id})")

    # Start web dashboard
    if DASHBOARD_ENABLED:
        try:
            start_dashboard(port=DASHBOARD_PORT)
            logger.info(f"📊 Dashboard: http://0.0.0.0:{DASHBOARD_PORT}")
        except Exception as e:
            logger.error(f"❌ Dashboard failed: {e}")

    # Load plugins (self-healing)
    logger.info("📦 Loading plugins...")
    plugin_manager = PluginManager(app, modules_dir="modules")
    plugin_manager.load_all()

    loaded = len(plugin_manager.loaded)
    failed = len(plugin_manager.failed)
    logger.info(f"✅ Plugins loaded: {loaded} | Failed: {failed}")

    if failed:
        for name, err in plugin_manager.failed.items():
            logger.warning(f"   ❌ {name}: {err}")

    # Notify owner
    try:
        uptime_str = "just started"
        await app.send_message(
            OWNER_ID,
            f"🚀 <b>{BOT_NAME} is online!</b>\n\n"
            f"👤 <b>Account:</b> {me.mention}\n"
            f"📦 <b>Plugins:</b> <code>{loaded}</code> loaded, <code>{failed}</code> failed\n"
            f"🌐 <b>Proxy:</b> {'ON' if PROXY.get('hostname') else 'OFF'}\n"
            f"📊 <b>Dashboard:</b> {'ON' if DASHBOARD_ENABLED else 'OFF'}\n"
            f"⏱ <b>Started:</b> {uptime_str}",
        )
    except Exception as e:
        logger.warning(f"⚠️ Could not notify owner: {e}")

# ═══════════════════════════════════════════════════════════════
#  SHUTDOWN HANDLER
# ═══════════════════════════════════════════════════════════════
async def shutdown(sig=None):
    """Graceful shutdown."""
    if _shutdown_event.is_set():
        return
    _shutdown_event.set()

    logger.info(f"🛑 Shutting down (signal={sig})...")

    try:
        if app and app.is_connected:
            me = await app.get_me()
            try:
                await app.send_message(OWNER_ID, "🔴 <b>Userbot stopped.</b>")
            except Exception:
                pass
            await app.stop()
            logger.info("✅ Client stopped cleanly")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

    logger.info("👋 Goodbye!")

def signal_handler(sig, frame):
    """Sync signal handler → schedule async shutdown."""
    logger.info(f"📡 Signal received: {sig}")
    asyncio.create_task(shutdown(sig))

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
async def main():
    global app

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Build client
    app = create_client()

    # Startup
    await startup()

    # Keep running until shutdown
    try:
        await _shutdown_event.wait()
    except asyncio.CancelledError:
        await shutdown()

# ═══════════════════════════════════════════════════════════════
#  CRASH RECOVERY LOOP
# ═══════════════════════════════════════════════════════════════
def run_with_recovery():
    """Auto-restart on crash (max 5 times)."""
    max_retries = 5
    retry_delay = 10

    for attempt in range(1, max_retries + 1):
        try:
            asyncio.run(main())
            break  # Clean exit
        except KeyboardInterrupt:
            logger.info("⌨️  Interrupted by user")
            break
        except Exception as e:
            logger.critical(f"💥 Crash (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                logger.info(f"⏳ Restarting in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.critical("❌ Max retries reached. Exiting.")
                sys.exit(1)

# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Ensure directories exist
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    run_with_recovery()