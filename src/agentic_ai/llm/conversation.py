from ollama import chat
from agentic_ai.model_config import MODEL


class Conversation:
    def __init__(self):
        self.messages = []

    def ask(self, prompt: str) -> str:
        self.messages.append({
            "role": "system",
            "content": "You are a Java tutor. Answer concisely using java examples."   
        })

        response = chat(
            model=MODEL,
            messages=self.messages
        )

        answer = response.message.content

        self.messages.append({
            "role" : "user",
            "content" : answer
        })

        return answer