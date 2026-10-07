"""
Agentic AI with Tools
- AI sees all available tools
- Decides which tool to call based on user query
- Supports multiple providers (OpenAI, Gemini, Groq)
"""
import json
import aiohttp
from typing import Callable

class Agent:
    def __init__(self, api_key, model="gpt-4o-mini", provider="openai"):
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.tools = {}  # {name: {func, description, params}}

    def register_tool(self, name, description, params, func):
        """Register a tool the AI can call."""
        self.tools[name] = {
            "func": func,
            "description": description,
            "params": params,
        }

    def get_tool_definitions(self):
        """Generate OpenAI function-calling schema."""
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": t["description"],
                    "parameters": {
                        "type": "object",
                        "properties": t["params"],
                        "required": list(t["params"].keys()),
                    },
                },
            }
            for name, t in self.tools.items()
        ]

    async def run(self, user_query, max_iterations=5):
        """Run agent loop: think → call tool → observe → answer."""
        messages = [{"role": "user", "content": user_query}]

        for iteration in range(max_iterations):
            # Call LLM
            response = await self._call_llm(messages)
            
            # Check if tool call requested
            if response.get("tool_calls"):
                for tc in response["tool_calls"]:
                    func_name = tc["function"]["name"]
                    args = json.loads(tc["function"]["arguments"])
                    
                    # Execute tool
                    tool = self.tools.get(func_name)
                    if tool:
                        try:
                            result = await tool["func"](**args)
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "content": str(result),
                            })
                        except Exception as e:
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "content": f"Error: {e}",
                            })
            else:
                # Final answer
                return response.get("content", "")

        return "Max iterations reached."

    async def _call_llm(self, messages):
        """Call OpenAI-compatible API."""
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": self.get_tool_definitions() or None,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
            ) as r:
                data = await r.json()
        
        choice = data["choices"][0]["message"]
        return {
            "content": choice.get("content", ""),
            "tool_calls": choice.get("tool_calls", []),
        }