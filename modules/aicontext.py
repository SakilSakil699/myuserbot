from helpers import cmd
from config import OPENAI_API_KEY
import aiohttp

def register(app):
    @app.on_message(cmd("sum"))
    async def summarize(client, message):
        """
        .sum [count] [question]
        Example: .sum 100 What was decided about the project?
        """
        args = message.text.split(None, 2)
        count = 100
        question = None
        
        if len(args) >= 2 and args[1].isdigit():
            count = min(int(args[1]), 500)
        if len(args) >= 3:
            question = args[2]

        await message.edit(f"📖 Reading last {count} messages...")
        
        # Fetch chat history
        history = []
        async for msg in app.get_chat_history(message.chat.id, limit=count):
            if msg.text and msg.from_user:
                history.append(f"{msg.from_user.first_name}: {msg.text}")
        
        if not history:
            return await message.edit("❌ No messages found.")

        context = "\n".join(reversed(history))
        
        if question:
            prompt = f"Based on this chat context, answer: {question}\n\nContext:\n{context}"
        else:
            prompt = f"Summarize this chat conversation in 5-7 bullet points:\n\n{context}"

        # Call AI
        await message.edit("🧠 Analyzing...")
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
        }
        
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload, headers=headers,
            ) as r:
                data = await r.json()
        
        reply = data["choices"][0]["message"]["content"]
        await message.edit(f"📝 <b>Summary:</b>\n\n{reply}")