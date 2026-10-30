from agentic_ai.agents.travel_agent import TravelAgent

def main():
    session_id = input("Session ID [travel-demo]: ").strip();
    session_id = session_id or "travel-demo"

    agent = TravelAgent(session_id)

    print("Travel Agent started. Type exit to quit. \n")

    while True:

        request = input("You: ")

        if request.lower() == "exit":
            print("Exiting Travel Agent.")
            break

        answer = agent.ask(request)

        print(f"\nAI: {answer}\n")

if __name__ == "__main__":
    main()