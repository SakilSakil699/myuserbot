import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram ────────────────────────────────────────────
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ── Bot Config ──────────────────────────────────────────
BOT_NAME = os.getenv("BOT_NAME", "Ultimate Userbot")
PREFIX = os.getenv("PREFIX", ".")

# ── Security ────────────────────────────────────────────
VAULT_KEY = os.getenv("VAULT_KEY", "")

# ── Proxy (optional) ────────────────────────────────────
PROXY = None
if os.getenv("PROXY_HOST"):
    PROXY = {
        "scheme": os.getenv("PROXY_SCHEME", "socks5"),
        "hostname": os.getenv("PROXY_HOST"),
        "port": int(os.getenv("PROXY_PORT", "1080")),
        "username": os.getenv("PROXY_USER") or None,
        "password": os.getenv("PROXY_PASS") or None,
    }

# ── Dashboard ───────────────────────────────────────────
DASHBOARD_ENABLED = os.getenv("DASHBOARD_ENABLED", "true").lower() == "true"
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8080"))

# ── API Keys ────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")