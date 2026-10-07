from helpers import cmd
from core.agent import Agent
from config import OPENAI_API_KEY, OWNER_ID
import os

agent = Agent(OPENAI_API_KEY)

# Register your existing modules as tools!
def register_tools():
    # Example: register crypto price tool
    async def get_crypto_price(coin: str):
        import aiohttp
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,inr"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                return await r.json()

    agent.register_tool(
        "get_crypto_price",
        "Get current price of a cryptocurrency by name (e.g. bitcoin, ethereum)",
        {"coin": {"type": "string", "description": "Coin name"}},
        get_crypto_price,
    )

    # Example: weather tool
    async def get_weather(city: str):
        import aiohttp
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://wttr.in/{city}?format=3") as r:
                return await r.text()

    agent.register_tool(
        "get_weather",
        "Get weather for a city",
        {"city": {"type": "string"}},
        get_weather,
    )

def register(app):
    register_tools()

    @app.on_message(cmd("ask"))
    async def ask_agent(client, message):
        args = message.text.split(None, 1)
        if len(args) < 2:
            return await message.edit("⚠️ <code>.ask your question</code>")
        
        await message.edit("🤖 Thinking...")
        try:
            answer = await agent.run(args[1])
            await message.edit(f"🤖 <b>AI:</b>\n\n{answer}")
        except Exception as e:
            await message.edit(f"❌ Error: {e}")