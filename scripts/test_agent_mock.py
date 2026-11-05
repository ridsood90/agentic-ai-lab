from agentic_ai.agents.travel_agent import TravelAgent
from agentic_ai.memory.state_extractor import StateUpdate
from ollama import ChatResponse, Message

class FakeChatClient:

    def __init__(self):
        self.call_count = 0

    def __call__(self, **kwargs):
        self.call_count += 1

        if self.call_count == 1:
            return ChatResponse(
                model = "qwen3:8b",
                message=Message(
                    role="assistant",
                    content="",
                    tool_calls=[
                        {
                            "function": {
                                "name": "search_flights",
                                "arguments": {"destination": "Paris"}
                            }
                        }
                    ]
                ),
                done=True,
            )

        return ChatResponse(
            model = "qwen3:8b",
            message=Message(
                role="assistant",
                content="I found flights to Paris.",
            ),
            done=True
        )

class FakeStateExtractor:

    def extract(self, user_message, current_state):
        return StateUpdate( state_update={"destination": "Paris"})

class FakeSummarizer:

    def summarize(self, previous_summary, messages):
        return previous_summary

fake_llm = FakeChatClient()

agent = TravelAgent(
    session_id="mock-test-2",
    chat_client=fake_llm
)
agent.state_extractor = FakeStateExtractor()
agent.summarizer = FakeSummarizer()

answer = agent.ask("Find flights to Paris")
print("Answer: ", answer)
print("LLM calls: ", fake_llm.call_count)