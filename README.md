<div align="center">

# 🚀 Ultimate Advanced Userbot

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=28&duration=3000&pause=1000&color=7C5CFF&center=true&vCenter=true&multiline=true&width=700&height=100&lines=Self-Healing+Plugin+Manager;Locked+Session+Protocol;Agentic+AI+with+Tools;Zero-Downtime+Updates" alt="Typing SVG" />

**Production-grade Telegram userbot with self-healing architecture, encrypted sessions, and AI-powered automation.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0.106-7C5CFF?style=for-the-badge)](https://pyrogram.org)
[![Termux](https://img.shields.io/badge/Termux-Ready-000000?style=for-the-badge&logo=termux)](https://termux.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-success?style=for-the-badge)]()

</div>

---

## 📖 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📱 Termux Setup](#-termux-setup)
- [🔧 Configuration](#-configuration)
- [📚 Commands](#-commands)
- [🔐 Security](#-security)
- [🧩 Modules](#-modules)
- [🐛 Troubleshooting](#-troubleshooting)
- [⚠️ Disclaimer](#️-disclaimer)
- [📜 License](#-license)

---

## ✨ Features

### 🏗️ Core Architecture

| Feature | Description |
|---------|-------------|
| 🔄 **Self-Healing Plugins** | Auto-scans code, installs missing dependencies, recovers from crashes |
| 🔐 **Locked Session Protocol** | AES-128 encrypted sessions via Fernet — stolen sessions are useless |
| ⚡ **Self-Updating** | Pull updates from GitHub without losing config or data |
| 🛡️ **Crash Recovery** | Auto-restart with exponential backoff (max 5 retries) |
| 🌐 **SOCKS5 Proxy** | Native MTProto proxy support |
| 📦 **Modular Registry** | Each module independent, hot-reloadable |

### 🤖 AI Ecosystem

| Feature | Description |
|---------|-------------|
| 🧠 **Agentic AI** | AI decides which tool to call based on user query |
| 📝 **AIContext Summarizer** | Summarize chats, ask questions about conversation history |
| 🔀 **Multi-Model Support** | OpenAI + Gemini + Groq with automatic fallback |
| 🎨 **Image Generation** | DALL-E / SDXL integration |

### 🎁 Automation

| Feature | Description |
|---------|-------------|
| 🎯 **Gift Sniper** | Millisecond-precision Telegram Gift claiming |
| 💰 **Auto-Buy Gifts** | Filter by price/supply, auto-purchase |
| ⏰ **Scheduled Messages** | Redis-based reliable queue |
| 🔀 **Auto-Forward** | Channel → Group with content filters |

### 🛡️ Security

| Feature | Description |
|---------|-------------|
| 🔐 **Session Vault** | Fernet-encrypted session storage |
| 🕵️ **Anti-Hack Detection** | Alert on suspicious session usage |
| 🔒 **Chmod 600** | Auto-locks sensitive files |
| 🚫 **PM Permit** | Verification button for unknown users |
| 🛡️ **Anti-Flood** | Auto-mute spammers |
| 🚨 **Anti-Fraud** | Detect and remove scam links |

### 📊 Monitoring

| Feature | Description |
|---------|-------------|
| 📈 **Web Dashboard** | FastAPI-based UI (optional) |
| 📊 **Usage Analytics** | Track command frequency |
| 🚨 **Error Severity Logging** | Categorized error tracking |
| 💻 **System Stats** | CPU, RAM, disk monitoring |

---

## 🏗️ Architecture

```
myuserbot/
│
├── 📄 main.py                  Entry point
├── 📄 config.py                Config loader
├── 📄 gen_session.py           Session generator (advanced)
├── 📄 requirements.txt
├── 📄 .env                     Secrets (not committed)
├── 📄 .env.example             Template
├── 📄 .gitignore
├── 📄 README.md
│
├── 📂 core/                    Core systems
│   ├── __init__.py
│   ├── logger.py               Colored logger
│   ├── session_vault.py        🔐 Encryption
│   ├── plugin_manager.py       🔄 Self-healing
│   ├── updater.py              ⚡ Auto-update
│   ├── agent.py                🧠 Agentic AI
│   └── web_dashboard.py        📊 Dashboard
│
├── 📂 modules/                 Bot commands
│   ├── __init__.py
│   ├── utils.py                Basic commands
│   ├── afk.py                  AFK system
│   ├── notes.py                Note storage
│   ├── filters.py              Keyword replies
│   ├── pm_permit.py            PM security
│   ├── groupmanager.py         Admin tools
│   ├── gpt.py                  AI chat
│   ├── crypto.py               Price tracker
│   └── ... (40+ modules)
│
├── 📂 data/                    JSON databases
├── 📂 logs/                    Log files
└── 📂 sessions/                Saved sessions
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Telegram account
- API credentials from [my.telegram.org](https://my.telegram.org)

### 1. Clone / Setup

```bash
git clone https://github.com/YOUR_USERNAME/myuserbot.git
cd myuserbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
nano .env
```

Fill in `API_ID`, `API_HASH`, `OWNER_ID`, `VAULT_KEY`.

### 4. Generate Session

```bash
python gen_session.py --name main --yes
```

### 5. Run

```bash
python main.py
```

---

## 📱 Termux Setup

### Install Termux

Download from [F-Droid](https://f-droid.org/en/packages/com.termux/) — **NOT** Play Store.

### One-Shot Install

```bash
pkg update && pkg upgrade -y
pkg install -y python python-pip git nano curl wget openssl libffi rust clang make binutils ca-certificates tmux

# Termux-specific heavy packages
pkg install -y python-pillow python-cryptography python-psutil python-lxml

# Pip packages
pip install --break-system-packages pyrogram tgcrypto python-dotenv aiohttp requests qrcode gTTS beautifulsoup4 pytz

# Storage access
termux-setup-storage

# Wakelock
termux-wake-lock
```

### Run in Background

```bash
tmux new -s bot
cd ~/myuserbot
python main.py
# Detach: Ctrl+B, then D
# Reattach: tmux attach -t bot
```

### Auto-Start on Boot

```bash
mkdir -p ~/.termux/boot
nano ~/.termux/boot/start-bot.sh
```

```bash
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
cd ~/myuserbot
nohup python main.py > bot.log 2>&1 &
```

```bash
chmod +x ~/.termux/boot/start-bot.sh
```

Install [Termux:Boot](https://f-droid.org/packages/com.termux.boot/).

---

## 🔧 Configuration

### `.env` Template

```env
# ═══ Telegram (Required) ═══
API_ID=123456
API_HASH=your_api_hash
SESSION_STRING=gAAAAAB...
OWNER_ID=123456789

# ═══ Bot Settings ═══
BOT_NAME=Ultimate Userbot
PREFIX=.
COMMAND_DELETE_AFTER=0

# ═══ Security (Recommended) ═══
VAULT_KEY=your-32-char-random-string

# ═══ Proxy (Optional) ═══
# PROXY_SCHEME=socks5
# PROXY_HOST=127.0.0.1
# PROXY_PORT=1080

# ═══ Dashboard (Optional) ═══
DASHBOARD_ENABLED=false
DASHBOARD_PORT=8080

# ═══ AI APIs (Optional) ═══
OPENAI_API_KEY=sk-xxx
GEMINI_API_KEY=
GROQ_API_KEY=

# ═══ Other (Optional) ═══
VIRUSTOTAL_API_KEY=
```

### Generate `VAULT_KEY`

```bash
python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
```

---

## 📚 Commands

<details>
<summary><b>🔧 Utility</b></summary>

| Command | Description |
|---------|-------------|
| `.ping` | Check latency and uptime |
| `.help` | Show all commands |
| `.id` | Get user/chat ID |
| `.info` | Detailed user info |
| `.stats` | System statistics |
| `.sysinfo` | OS, CPU, RAM info |

</details>

<details>
<summary><b>😴 AFK System</b></summary>

| Command | Description |
|---------|-------------|
| `.afk [reason]` | Set AFK status |
| `.unafk` | Remove AFK |

</details>

<details>
<summary><b>📝 Notes</b></summary>

| Command | Description |
|---------|-------------|
| `.save <name> <text>` | Save note |
| `.get <name>` | Retrieve note |
| `.notes` | List all notes |
| `.delnote <name>` | Delete note |

</details>

<details>
<summary><b>🛡️ Security</b></summary>

| Command | Description |
|---------|-------------|
| `.pmguard on/off` | Toggle PM permit |
| `.approve` | Approve user (reply) |
| `.antiflood on/off` | Toggle flood protection |
| `.antifraud on/off` | Toggle scam detection |
| `.antidelete on/off` | Toggle deleted message logger |

</details>

<details>
<summary><b>👑 Group Management</b></summary>

| Command | Description |
|---------|-------------|
| `.ban` `.unban` `.kick` | Member management |
| `.mute` `.unmute` | Restrict member |
| `.warn` | Warning system (3 = ban) |
| `.pin` | Pin message |
| `.promote` `.demote` | Admin management |
| `.tagall <note>` | Mention all members |
| `.purge` | Bulk delete (reply to first) |

</details>

<details>
<summary><b>🤖 AI</b></summary>

| Command | Description |
|---------|-------------|
| `.ai <question>` | Ask GPT |
| `.ask <question>` | Agentic AI with tools |
| `.sum [count] [q]` | Summarize chat |

</details>

<details>
<summary><b>🎁 Automation</b></summary>

| Command | Description |
|---------|-------------|
| `.snipe on/off` | Gift Sniper |
| `.schedule <time> <text>` | Schedule message |
| `.remind <time> <text>` | Reminder |
| `.autofw` | Auto-forward setup |
| `.autodel <sec>` | Auto-delete own messages |

</details>

<details>
<summary><b>🎨 Fun & Utility</b></summary>

| Command | Description |
|---------|-------------|
| `.weather <city>` | Weather report |
| `.tr <lang> <text>` | Translate |
| `.tts [lang] <text>` | Text to speech |
| `.qr <text>` | QR code generator |
| `.quote` | Quote image (reply) |
| `.short <url>` | URL shortener |
| `.price <coin>` | Crypto price |

</details>

<details>
<summary><b>🔐 Vault</b></summary>

| Command | Description |
|---------|-------------|
| `.vault save <name> <data>` | Save encrypted password |
| `.vault get <name>` | Retrieve |
| `.vault list` | List all |
| `.vault del <name>` | Delete |

</details>

<details>
<summary><b>📥 Downloaders</b></summary>

| Command | Description |
|---------|-------------|
| `.yt <url>` | YouTube download |
| `.ig <url>` | Instagram download |

</details>

---

## 🔐 Security

### Session Vault

Your session string is encrypted with **Fernet (AES-128 in CBC mode)**.

```
VAULT_KEY → SHA256 → Fernet Key → Encrypt(Session)
```

A stolen encrypted session **cannot be used** without your `VAULT_KEY`.

### Best Practices

- ✅ **Always** use encrypted sessions (`VAULT_KEY` set)
- ✅ Use `.env` with `chmod 600`
- ✅ Add `.env` to `.gitignore`
- ✅ Generate session **only on your own device**
- ✅ Enable 2FA on Telegram
- ✅ Rotate sessions every 6 months
- ✅ Use dedicated secondary account
- ❌ **Never** share session string
- ❌ **Never** commit `.env` to Git
- ❌ **Never** use random online session generators

### Session Rotation

```bash
# Every 6 months:
# 1. Terminate all sessions in Telegram → Settings → Devices
# 2. Generate new session
python gen_session.py --name main --yes
# 3. Restart bot
```

---

## 🧩 Modules

Want to add a new module? Create `modules/mycommand.py`:

```python
from helpers import cmd
from pyrogram import filters

def register(app):
    @app.on_message(cmd("hello"))
    async def hello(client, message):
        await message.edit("👋 Hello world!")
```

The **Self-Healing Plugin Manager** will:
1. Scan for imports
2. Auto-install missing dependencies
3. Register handlers
4. Log success/failure

**Hot reload** (no restart):
```python
from core.plugin_manager import PluginManager
pm = PluginManager(app)
pm.reload_plugin("mycommand")
```

---

## 🐛 Troubleshooting

<details>
<summary><b>❌ <code>externally-managed-environment</code></b></summary>

Termux uses PEP 668. Use:

```bash
pip install --break-system-packages <package>
```

</details>

<details>
<summary><b>❌ <code>platform android is not supported</code></b></summary>

Some packages (psutil, lxml) don't build on Termux. Use Termux packages:

```bash
pkg install python-psutil python-lxml
```

</details>

<details>
<summary><b>❌ <code>RuntimeError: no current event loop</code></b></summary>

Python 3.14 compatibility. Add to top of your script:

```python
import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
```

</details>

<details>
<summary><b>❌ <code>AuthKeyUnregistered</code></b></summary>

Session revoked. Regenerate:

```bash
python gen_session.py --name main --yes
```

</details>

<details>
<summary><b>❌ <code>FloodWait</code></b></summary>

Telegram rate limit. **Wait** the specified seconds. Do not retry immediately.

</details>

<details>
<summary><b>❌ Bot stops in Termux when screen off</b></summary>

```bash
termux-wake-lock
```

Also disable battery optimization for Termux:
**Settings → Apps → Termux → Battery → Unrestricted**

</details>

<details>
<summary><b>❌ <code>SessionPasswordNeeded</code> but no password works</b></summary>

Your 2FA password. If forgotten, reset it via Telegram.

</details>

<details>
<summary><b>❌ Dashboard not accessible</b></summary>

Install FastAPI:

```bash
pip install --break-system-packages fastapi uvicorn
```

Or disable in `.env`:

```env
DASHBOARD_ENABLED=false
```

</details>

---

## 🛣️ Roadmap

- [x] Self-Healing Plugins
- [x] Locked Session Protocol
- [x] Session Vault
- [x] Crash Recovery
- [x] Agentic AI
- [x] AIContext Summarizer
- [ ] Web Dashboard (full)
- [ ] Gift Sniper (production)
- [ ] Multi-account support
- [ ] Redis-backed scheduler
- [ ] Prometheus metrics
- [ ] Docker compose
- [ ] Natural language reminders
- [ ] Image generation

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing`
3. Commit: `git commit -m "Add amazing feature"`
4. Push: `git push origin feature/amazing`
5. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Test before submitting

---

## ⚠️ Disclaimer

**This project is for EDUCATIONAL PURPOSES ONLY.**

- ❌ Using userbots violates [Telegram's Terms of Service](https://telegram.org/tos)
- ⚠️ Your account **may be banned**
- 🚫 **Do not** use for spam, harassment, or illegal activities
- 🛡️ Use **only** on your own accounts
- 📜 Authors are **not responsible** for any misuse or consequences

**Use at your own risk.**

---

## 📜 License

```
MIT License

Copyright (c) 2025 Ultimate Userbot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

### ⭐ Agar useful lage, star dena!

**Made with ❤️ by [Your Name](https://github.com/YOUR_USERNAME)**

[⬆ Back to Top](#-ultimate-advanced-userbot)

</div>
