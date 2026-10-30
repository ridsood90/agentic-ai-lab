from agentic_ai.llm.client import ask_llm

def main():
    prompt = """
Explain microservices architecture.

Include:
1. Service discovery
2. API gateways
3. Distributed transactions
4. Event-driven communication
5. Database per service
"""

    answer = ask_llm(prompt)

    print("\n LLM Response: \n")
    print(answer)

if __name__ == "__main__":
    main()