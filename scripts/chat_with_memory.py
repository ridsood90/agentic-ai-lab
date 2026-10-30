from agentic_ai.llm.conversation import Conversation

def main():
    conversation = Conversation()

    print("Chat started. Type 'exit' to quit. \n")

    while True:
        prompt = input("You: ")

        if prompt.lower() == "exit":
            print("Exiting chat.")
            break

        answer = conversation.ask(prompt)
        print(f"\n LLM: {answer}\n")

if __name__ == "__main__":
    main()