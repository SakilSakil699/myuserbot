"""
Simple Flask/FastAPI dashboard
- Login via Telegram Web
- View stats
- Manage modules
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
import threading

dashboard = FastAPI()

@dashboard.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>Userbot Dashboard</title>
    <style>
        body { background: #0a0a0f; color: #fff; font-family: sans-serif; padding: 40px; }
        .card { background: #16162a; padding: 20px; border-radius: 12px; margin: 10px 0; }
        h1 { color: #7c5cff; }
    </style>
    </head>
    <body>
        <h1>🚀 Userbot Dashboard</h1>
        <div class="card"><b>Status:</b> 🟢 Online</div>
        <div class="card"><b>Modules:</b> 40+</div>
        <div class="card"><b>Uptime:</b> Loading...</div>
    </body>
    </html>
    """

def start_dashboard(port=8080):
    def run():
        uvicorn.run(dashboard, host="0.0.0.0", port=port, log_level="error")
    threading.Thread(target=run, daemon=True).start()