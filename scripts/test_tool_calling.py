from ollama import chat
from agentic_ai.tools.flight_tool import search_flights

messages = [
    {
        "role": "user",
        "content": "Find flights to Amsterdam"
    }
]

response = chat(
    model="qwen3:8b",
    messages=messages,
    tools = [search_flights]
)

messages.append(response.message)

for tool_call in response.message.tool_calls or []:
    if tool_call.function.name == "search_flights":
        result  = search_flights(**tool_call.function.arguments)
        messages.append(
            {
                "role" : "tool",
                "tool_name": "search_flights",
                "content": result
            }
        )

        print("Tool executed: ", result)

    if response.message.tool_calls:
        final_response = chat(
            model="qwen3:8b",
            messages=messages
        )
        print("AI:", final_response.message.content)
    else:
        print("AI:", response.message.content)

    