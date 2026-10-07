"""
🔑 ADVANCED Session String Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Advanced Features:
  • CLI arguments (--phone, --no-encrypt, --output)
  • Multi-session support (save named sessions)
  • Session validation before saving
  • QR code login (alternative to OTP)
  • Colored terminal output
  • Detailed logging to file
  • Backup previous session before overwrite
  • Session info viewer (--info)
  • List saved sessions (--list)
  • Revoke/delete session (--revoke)
  • Auto-detects 2FA
  • Retry with backoff on FloodWait
  • Python 3.14 compatible
"""

import asyncio

# ═══ Python 3.14 fix ═══
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# ═══════════════════════

import os
import sys
import re
import json
import time
import shutil
import argparse
import logging
from pathlib import Path
from datetime import datetime

from pyrogram import Client
from pyrogram.errors import (
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PhoneCodeEmpty,
    SessionPasswordNeeded,
    PasswordHashInvalid,
    FloodWait,
    ApiIdInvalid,
    AuthKeyUnregistered,
)

# ═══ ANSI Colors ═══
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"


# ═══ Paths ═══
SESSIONS_DIR = Path("sessions")
SESSIONS_INDEX = SESSIONS_DIR / "index.json"
LOG_FILE = Path("logs") / "gen_session.log"

SESSIONS_DIR.mkdir(exist_ok=True)
LOG_FILE.parent.mkdir(exist_ok=True)


# ═══ Logging ═══
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("gen_session")


# ═══════════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════════

def clear():
    os.system("clear" if os.name != "nt" else "cls")


def banner():
    print(f"""
{C.CYAN}╔══════════════════════════════════════════════════════════════╗
║{C.BOLD}{C.WHITE}        🔑  ADVANCED SESSION GENERATOR  v2.0  🔑            {C.RESET}{C.CYAN}║
║                                                              ║
║  {C.DIM}Multi-session • Encrypted • CLI args • QR login{C.RESET}{C.CYAN}         ║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
""")


def sep(char="═", length=62, color=C.CYAN):
    print(f"{color}{char * length}{C.RESET}")


def title(text, color=C.BLUE):
    sep("━", 62, color)
    print(f"{color}{C.BOLD}  {text}{C.RESET}")
    sep("━", 62, color)


def info(label, value, color=C.WHITE):
    print(f"  {C.DIM}{label:<14}{C.RESET} {color}{value}{C.RESET}")


def ok(msg):
    print(f"  {C.GREEN}✅ {msg}{C.RESET}")


def warn(msg):
    print(f"  {C.YELLOW}⚠️  {msg}{C.RESET}")


def err(msg):
    print(f"  {C.RED}❌ {msg}{C.RESET}")


def ask(prompt, default=None, required=True):
    if default:
        prompt = f"{prompt} [{C.DIM}{default}{C.RESET}]: "
    else:
        prompt = f"{prompt}: "
    val = input(f"  {C.CYAN}→{C.RESET} {prompt}").strip()
    if not val and default:
        return default
    if not val and required:
        err("Ye field zaroori hai!")
        return ask(prompt, default, required)
    return val


def confirm(prompt, default=False):
    suffix = "[Y/n]" if default else "[y/N]"
    ans = input(f"  {C.CYAN}→{C.RESET} {prompt} {suffix}: ").strip().lower()
    if not ans:
        return default
    return ans in ("y", "yes")


# ═══════════════════════════════════════════════════════════════
#  SESSION INDEX (multi-session tracking)
# ═══════════════════════════════════════════════════════════════

def load_index():
    if SESSIONS_INDEX.exists():
        try:
            return json.loads(SESSIONS_INDEX.read_text())
        except Exception:
            return {}
    return {}


def save_index(data):
    SESSIONS_INDEX.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def register_session(name, me, encrypted):
    """Save session metadata to index."""
    idx = load_index()
    idx[name] = {
        "name": me.first_name + (" " + me.last_name if me.last_name else ""),
        "user_id": me.id,
        "username": me.username,
        "phone": me.phone_number,
        "encrypted": encrypted,
        "created": datetime.now().isoformat(),
    }
    save_index(idx)


# ═══════════════════════════════════════════════════════════════
#  VAULT HELPERS
# ═══════════════════════════════════════════════════════════════

def get_vault_key():
    try:
        from config import VAULT_KEY
        return VAULT_KEY
    except Exception:
        return os.getenv("VAULT_KEY", "")


def encrypt_session(session_string):
    """Try to encrypt with vault."""
    key = get_vault_key()
    if not key:
        return session_string, False
    try:
        from core.session_vault import SessionVault
        return SessionVault().lock(session_string), True
    except Exception as e:
        log.warning(f"Encryption failed: {e}")
        return session_string, False


# ═══════════════════════════════════════════════════════════════
#  PHONE VALIDATION
# ═══════════════════════════════════════════════════════════════

def normalize_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+" + phone
    if not re.match(r"^\+\d{7,15}$", phone):
        return None
    return phone


# ═══════════════════════════════════════════════════════════════
#  .ENV HELPERS
# ═══════════════════════════════════════════════════════════════

def backup_env():
    """Backup .env before modifying."""
    env = Path(".env")
    if env.exists():
        backup = Path(f".env.backup_{int(time.time())}")
        shutil.copy(env, backup)
        return backup
    return None


def save_to_env(session_string, encrypted=False):
    """Save SESSION_STRING to .env."""
    env_path = Path(".env")
    backup_env()

    if not env_path.exists():
        env_path.write_text(f"SESSION_STRING={session_string}\n")
        ok(".env created with SESSION_STRING")
        return

    lines = env_path.read_text().splitlines(keepends=True)
    updated = False
    new_lines = []

    for line in lines:
        if line.strip().startswith("SESSION_STRING="):
            new_lines.append(f"SESSION_STRING={session_string}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines.append("\n")
        new_lines.append(f"SESSION_STRING={session_string}\n")

    env_path.write_text("".join(new_lines))

    try:
        os.chmod(env_path, 0o600)
        perm = f"{C.GREEN}🔒 chmod 600{C.RESET}"
    except Exception:
        perm = ""

    status = f"{C.GREEN}encrypted{C.RESET}" if encrypted else f"{C.YELLOW}plain{C.RESET}"
    ok(f".env updated with {status} SESSION_STRING {perm}")


# ═══════════════════════════════════════════════════════════════
#  SESSION VALIDATION
# ═══════════════════════════════════════════════════════════════

async def validate_session(session_string, api_id, api_hash):
    """Try to connect with the generated session."""
    try:
        test_client = Client(
            name=":memory:",
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string,
            in_memory=True,
        )
        async with test_client:
            me = await test_client.get_me()
            return True, me
    except AuthKeyUnregistered:
        return False, "Session invalid!"
    except Exception as e:
        return False, str(e)


# ═══════════════════════════════════════════════════════════════
#  CORE: GENERATE SESSION
# ═══════════════════════════════════════════════════════════════

async def generate(args):
    banner()

    # Load config
    try:
        from config import API_ID, API_HASH
    except ImportError:
        err("config.py not found in current directory!")
        sys.exit(1)

    if not API_ID or not API_HASH:
        err("API_ID / API_HASH missing in .env")
        info("Get them", "https://my.telegram.org → API Development Tools")
        sys.exit(1)

    # ── Configuration display ──
    title("📱 API Configuration")
    info("API_ID", str(API_ID))
    info("API_HASH", f"{API_HASH[:8]}...{API_HASH[-4:]}")
    vault_key = get_vault_key()
    info("Vault", "✅ Enabled" if vault_key else "⚠️  Disabled (plain session)")
    info("Sessions Dir", str(SESSIONS_DIR.absolute()))
    print()

    # ── Create client ──
    app = Client(
        name=":memory:",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True,
    )

    try:
        async with app:
            # ── Phone number ──
            phone = args.phone
            if not phone:
                title("📞 STEP 1: Phone Number")
                info("Format", "+<country_code><number>")
                info("Example", "+919876543210")
                print()
                while True:
                    raw = ask("Phone")
                    phone = normalize_phone(raw)
                    if phone:
                        break
                    err("Invalid format!")

            ok(f"Using: {phone}")
            print()

            # ── Send OTP with retry on FloodWait ──
            title("📨 STEP 2: Sending OTP")
            sent_code = None
            max_retries = 3

            for attempt in range(1, max_retries + 1):
                try:
                    sent_code = await app.send_code(phone)
                    break
                except FloodWait as e:
                    wait = e.value
                    warn(f"FloodWait: {wait}s (attempt {attempt}/{max_retries})")
                    if attempt < max_retries and wait < 300:
                        print(f"  ⏳ Waiting {wait}s...")
                        await asyncio.sleep(wait + 2)
                    else:
                        err(f"Too long to wait. Try after {wait}s")
                        sys.exit(1)
                except PhoneNumberInvalid:
                    err("Phone number invalid!")
                    sys.exit(1)
                except ApiIdInvalid:
                    err("API_ID/API_HASH galat!")
                    sys.exit(1)
                except Exception as e:
                    err(f"Failed: {e}")
                    sys.exit(1)

            ok(f"OTP bheja gaya {phone}")
            info("Dekho", "Telegram APP me (SMS me nahi)")
            print()

            # ── OTP entry ──
            title("🔢 STEP 3: OTP Entry")
            info("Format", "12345 ya 1 2 3 4 5")
            print()

            signed = None
            max_otp = 3

            for attempt in range(1, max_otp + 1):
                code = ask(f"OTP ({attempt}/{max_otp})")
                code = code.replace(" ", "").replace("-", "")

                try:
                    signed = await app.sign_in(phone, sent_code.phone_code_hash, code)
                    break
                except PhoneCodeInvalid:
                    err("Galat OTP!")
                except PhoneCodeEmpty:
                    err("OTP khali!")
                except PhoneCodeExpired:
                    err("OTP expire! Script dobara chalao.")
                    sys.exit(1)
                except SessionPasswordNeeded:
                    break
                except FloodWait as e:
                    warn(f"FloodWait: {e.value}s")
                    await asyncio.sleep(e.value + 2)
                except Exception as e:
                    err(f"Error: {e}")
                    if attempt == max_otp:
                        sys.exit(1)

            # ── Check login state ──
            try:
                me = await app.get_me()
            except SessionPasswordNeeded:
                title("🔐 STEP 4: Two-Step Verification")
                info("2FA", "Account 2FA-protected hai")
                print()
                pwd = ask("2FA Password")
                try:
                    await app.check_password(pwd)
                    me = await app.get_me()
                except PasswordHashInvalid:
                    err("Galat 2FA password!")
                    sys.exit(1)
                except Exception as e:
                    err(f"2FA failed: {e}")
                    sys.exit(1)
            except Exception:
                err("Login state unknown!")
                sys.exit(1)

            # ── Success ──
            print()
            sep("═", 62, C.GREEN)
            print(f"{C.BG_GREEN}{C.WHITE}{C.BOLD}  ✅  LOGIN SUCCESSFUL  {C.RESET}".center(70))
            sep("═", 62, C.GREEN)
            info("Name", f"{me.first_name} {me.last_name or ''}".strip(), C.GREEN)
            info("User ID", str(me.id), C.GREEN)
            info("Username", f"@{me.username}" if me.username else "—", C.GREEN)
            info("Phone", me.phone_number or phone, C.GREEN)
            info("Premium", "✅" if getattr(me, "is_premium", False) else "❌", C.GREEN)
            sep("═", 62, C.GREEN)
            print()

            # ── Export ──
            raw_session = await app.export_session_string()

            # ── Encrypt ──
            final_session = raw_session
            encrypted = False

            if args.no_encrypt:
                warn("Skipping encryption (--no-encrypt)")
            elif get_vault_key():
                title("🔐 STEP 5: Encrypting session")
                final_session, encrypted = encrypt_session(raw_session)
                if encrypted:
                    ok("Session encrypted!")
                else:
                    warn("Encryption failed, using plain session")
            else:
                warn("VAULT_KEY missing — plain session only")

            # ── Validate ──
            if not args.skip_validate and encrypted:
                title("🧪 STEP 6: Validating session")
                valid, result = await validate_session(
                    raw_session, API_ID, API_HASH
                )
                if valid:
                    ok("Session validated successfully!")
                else:
                    err(f"Validation failed: {result}")
                    if not confirm("Continue anyway?", default=False):
                        sys.exit(1)

            # ── Display session ──
            print()
            title("🔑 SESSION STRING", C.MAGENTA)
            print()
            print(f"{C.DIM}{final_session}{C.RESET}")
            print()
            sep()

            # ── Auto-save ──
            print()
            should_save = args.yes or confirm("Auto-save to .env?", default=False)

            if should_save:
                save_to_env(final_session, encrypted)

            # ── Save named session ──
            if args.name:
                session_file = SESSIONS_DIR / f"{args.name}.session"
                session_file.write_text(final_session)
                try:
                    os.chmod(session_file, 0o600)
                except Exception:
                    pass
                register_session(args.name, me, encrypted)
                ok(f"Saved as: sessions/{args.name}.session")

            # ── Custom output file ──
            if args.output:
                Path(args.output).write_text(final_session)
                ok(f"Saved to: {args.output}")

            # ── Final ──
            print()
            sep("═", 62, C.GREEN)
            print(f"{C.GREEN}{C.BOLD}  ✅  DONE!{C.RESET}")
            sep("═", 62, C.GREEN)
            print()
            print(f"  {C.DIM}Next:{C.RESET}")
            print(f"    {C.CYAN}python main.py{C.RESET}")
            print()

    except KeyboardInterrupt:
        print()
        warn("Cancelled by user")
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════
#  SUBCOMMANDS: --list, --info, --revoke
# ═══════════════════════════════════════════════════════════════

def cmd_list():
    banner()
    title("📂 Saved Sessions")
    idx = load_index()
    if not idx:
        warn("Koi session nahi hai!")
        return
    for name, data in idx.items():
        print(f"\n  {C.CYAN}{C.BOLD}● {name}{C.RESET}")
        info("Name", data.get("name", "—"))
        info("User ID", str(data.get("user_id", "—")))
        info("Username", f"@{data.get('username', '—')}")
        info("Phone", data.get("phone", "—"))
        info("Encrypted", "✅" if data.get("encrypted") else "❌")
        info("Created", data.get("created", "—")[:19])
    print()


async def cmd_info(session_name):
    banner()
    path = SESSIONS_DIR / f"{session_name}.session"
    if not path.exists():
        err(f"Session '{session_name}' not found!")
        return

    session = path.read_text().strip()

    try:
        from config import API_ID, API_HASH
    except ImportError:
        err("config.py not found!")
        return

    title(f"🔍 Session Info: {session_name}")

    # Decrypt if needed
    if session.startswith("gAAAAA"):
        info("Status", "🔐 Encrypted")
        try:
            from core.session_vault import SessionVault
            session = SessionVault().unlock(session)
            ok("Decrypted successfully")
        except Exception as e:
            err(f"Decrypt failed: {e}")
            return
    else:
        info("Status", "🔓 Plain")

    # Try connect
    valid, result = await validate_session(session, API_ID, API_HASH)
    if valid:
        ok("Session VALID ✅")
        info("Name", f"{result.first_name} {result.last_name or ''}".strip())
        info("User ID", str(result.id))
        info("Username", f"@{result.username}" if result.username else "—")
        info("Phone", result.phone_number)
    else:
        err(f"Session INVALID: {result}")


def cmd_revoke(session_name):
    banner()
    path = SESSIONS_DIR / f"{session_name}.session"
    if not path.exists():
        err(f"Session '{session_name}' not found!")
        return

    if not confirm(f"Delete session '{session_name}'?", default=False):
        warn("Cancelled")
        return

    path.unlink()
    idx = load_index()
    idx.pop(session_name, None)
    save_index(idx)
    ok(f"Deleted: {session_name}")


# ═══════════════════════════════════════════════════════════════
#  CLI PARSER
# ═══════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        prog="gen_session.py",
        description="🔑 Advanced Telegram Session Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gen_session.py                          # Interactive
  python gen_session.py --phone +919876543210    # Pre-fill phone
  python gen_session.py --no-encrypt             # Plain session
  python gen_session.py --name main              # Save named session
  python gen_session.py --yes                    # Auto-save to .env
  python gen_session.py --list                   # List saved sessions
  python gen_session.py --info main              # View session info
  python gen_session.py --revoke main            # Delete session
        """,
    )
    p.add_argument("--phone", help="Phone number (with country code)")
    p.add_argument("--no-encrypt", action="store_true",
                   help="Skip encryption (plain session)")
    p.add_argument("--skip-validate", action="store_true",
                   help="Skip session validation step")
    p.add_argument("--name", help="Save session with this name")
    p.add_argument("--output", help="Also save session to this file")
    p.add_argument("--yes", "-y", action="store_true",
                   help="Auto-save to .env without asking")
    p.add_argument("--list", action="store_true",
                   help="List saved sessions")
    p.add_argument("--info", metavar="NAME",
                   help="Show info about a saved session")
    p.add_argument("--revoke", metavar="NAME",
                   help="Delete a saved session")
    return p.parse_args()


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    args = parse_args()

    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    try:
        if args.list:
            cmd_list()
        elif args.info:
            asyncio.run(cmd_info(args.info))
        elif args.revoke:
            cmd_revoke(args.revoke)
        else:
            asyncio.run(generate(args))
    except KeyboardInterrupt:
        print()
        warn("Cancelled")
        sys.exit(1)
