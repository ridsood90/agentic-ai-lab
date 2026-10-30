from ollama import chat


class Conversation:
    def __init__(self):
        self.messages = []

    def ask(self, prompt: str) -> str:
        self.messages.append({
            "role": "system",
            "content": "You are a Java tutor. Answer concisely using java examples."   
        })

        response = chat(
            model="qwen3:8b",
            messages=self.messages
        )

        answer = response.message.content

        self.messages.append({
            "role" : "user",
            "content" : answer
        })

        return answer