"""
⚙️  Config loader for Ultimate Userbot
Reads from .env file
"""

import os
from dotenv import load_dotenv

# Load .env from root
load_dotenv()


# ═══════════════════════════════════════════════
#  🔑 TELEGRAM CREDENTIALS (required)
# ═══════════════════════════════════════════════

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

# Session string — plain OR encrypted (starts with gAAAAA)
SESSION_STRING = os.getenv("SESSION_STRING", "")

# Owner's Telegram user ID (get from @userinfobot)
OWNER_ID = int(os.getenv("OWNER_ID", "0"))


# ═══════════════════════════════════════════════
#  🤖 BOT SETTINGS
# ═══════════════════════════════════════════════

BOT_NAME = os.getenv("BOT_NAME", "Ultimate Userbot")
PREFIX = os.getenv("PREFIX", ".")

# How many seconds to auto-delete command messages (0 = never)
COMMAND_DELETE_AFTER = int(os.getenv("COMMAND_DELETE_AFTER", "0"))


# ═══════════════════════════════════════════════
#  🔐 SECURITY
# ═══════════════════════════════════════════════

# Master key for encrypting session strings
# Used by core/session_vault.py
VAULT_KEY = os.getenv("VAULT_KEY", "")


# ═══════════════════════════════════════════════
#  🌐 PROXY (optional)
# ═══════════════════════════════════════════════

PROXY = None
if os.getenv("PROXY_HOST"):
    PROXY = {
        "scheme": os.getenv("PROXY_SCHEME", "socks5"),
        "hostname": os.getenv("PROXY_HOST", ""),
        "port": int(os.getenv("PROXY_PORT", "1080")),
        "username": os.getenv("PROXY_USER") or None,
        "password": os.getenv("PROXY_PASS") or None,
    }


# ═══════════════════════════════════════════════
#  📊 WEB DASHBOARD (optional)
# ═══════════════════════════════════════════════

DASHBOARD_ENABLED = os.getenv("DASHBOARD_ENABLED", "false").lower() == "true"
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8080"))
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "")


# ═══════════════════════════════════════════════
#  🤖 AI API KEYS (optional)
# ═══════════════════════════════════════════════

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


# ═══════════════════════════════════════════════
#  🔍 OTHER APIs (optional)
# ═══════════════════════════════════════════════

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")


# ═══════════════════════════════════════════════
#  ⚙️  VALIDATION (warn on missing)
# ═══════════════════════════════════════════════

def validate():
    """Print warnings for missing required values."""
    missing = []
    if not API_ID:
        missing.append("API_ID")
    if not API_HASH:
        missing.append("API_HASH")
    if not SESSION_STRING:
        missing.append("SESSION_STRING")
    if not OWNER_ID:
        missing.append("OWNER_ID")

    if missing:
        print("⚠️  Missing in .env:")
        for m in missing:
            print(f"   • {m}")
        return False
    return True


# Auto-validate on import
if __name__ != "__main__":
    validate()
