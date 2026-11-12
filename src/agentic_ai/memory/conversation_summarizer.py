from ollama import chat
from agentic_ai.model_config import MODEL

class ConversationSummarizer:

    def summarize(self, previous_summary: str, messages: list) -> str:
        response = chat(
            model=MODEL,
            think=False,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You maintain a concise memory of a travel conversation. "
                        "Preserve destinations, dates, budgets, preferences, "
                        "constraints and unresolved requests. "
                        "Preserve important tool results as historical observations. "
                        "Do not invent information. "
                        "Do not treat mock prices as live availability. "
                        "Return only the updated summary."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Previous summary:\n{previous_summary}\n\n"
                        f"New conversation messages:\n{messages}"
                    )
                }
            ]
        )

        return response.message.content or previous_summary