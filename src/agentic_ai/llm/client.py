from ollama import chat
from agentic_ai.model_config import MODEL

def ask_llm(prompt: str) -> str:
    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user", 
                "content": prompt
            }
        ]
    )

    print("Input tokens:", response.prompt_eval_count)
    print("Output tokens:", response.eval_count)
    
    return response.message.content