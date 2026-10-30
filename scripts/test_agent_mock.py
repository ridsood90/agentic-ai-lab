from agentic_ai.agents.travel_agent import TravelAgent
from types import SimpleNamespace

class FakeChatClient:

    def __init__(self):
        self.call_count = 0

    def __call__(self, **kwargs):
        self.call_count += 1

        if self.call_count == 1:
            return SimpleNamespace(
                message=SimpleNamespace(
                    role="assistant",
                    content="",
                    tool_calls=[
                        SimpleNamespace(
                            function=SimpleNamespace(
                                name="search_flights",
                                arguments={"destination":"Paris"}
                            )
                        )
                    ]
                )
            )

        return SimpleNamespace(
            message=SimpleNamespace(
                role="assistant",
                content="I found flights to Paris.",
                tool_calls=None
            )
        )

    fake_llm = FakeChatClient()

    agent = TravelAgent(
        session_id="mock-test-1",
        chat_client=fake_llm
    )

    answer = agent.ask("Find flights to Paris")

    print("Answer: ", answer)
    print("LLM calls: ", fake_llm.call_count)