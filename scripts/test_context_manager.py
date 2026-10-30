from agentic_ai.memory.context_manager import ContextManager

messages = [
    {"role": "system", "content":"You are a travel assistant."}
]

for i in range(1, 11):
    messages.append({
        "role": "user",
        "content": f"Question {i}"
    })

    messages.append({
        "role": "assistant",
        "content": f"Answer {i}"
    })

manager = ContextManager(max_turns=3)
context = manager.build_context(messages)

for message in context:
    print(message["role"], ":", message["content"])