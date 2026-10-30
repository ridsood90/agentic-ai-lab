from ollama import chat

def ask_llm(prompt: str) -> str:
    response = chat(
        model="qwen3:8b",
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