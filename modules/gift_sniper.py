from helpers import cmd
from config import OWNER_ID
import asyncio
import aiohttp

SNIPING = False
FILTERS = {"max_price": 1000, "min_supply": 0}

def register(app):
    @app.on_message(cmd("snipe"))
    async def toggle_snipe(client, message):
        global SNIPING
        args = message.text.split()
        if len(args) > 1 and args[1] == "off":
            SNIPING = False
            return await message.edit("🛑 Gift Sniper OFF")
        
        SNIPING = True
        await message.edit("🎯 Gift Sniper ON\nMonitoring gifts...")
        
        async def monitor():
            while SNIPING:
                try:
                    # Use Telegram's gift API (Pyrogram method)
                    # Note: This requires Pyrogram to support get_available_gifts
                    # For now, using raw API call pattern
                    gifts = await client.invoke(
                        # Replace with actual gift method
                        # Example: GetAvailableStarGifts()
                    )
                    for gift in gifts:
                        if self._matches_filter(gift):
                            await self._claim(client, gift)
                except Exception as e:
                    print(f"Sniper error: {e}")
                await asyncio.sleep(2)
        
        asyncio.create_task(monitor())

    def _matches_filter(gift):
        price = getattr(gift, "stars", 999999)
        supply = getattr(gift, "supply", 0)
        return price <= FILTERS["max_price"] and supply >= FILTERS["min_supply"]

    async def _claim(client, gift):
        try:
            # Claim logic here
            await client.send_message(OWNER_ID, f"🎁 Gift claimed: {gift}")
        except Exception as e:
            await client.send_message(OWNER_ID, f"❌ Claim failed: {e}")