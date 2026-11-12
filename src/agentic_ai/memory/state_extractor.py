from agentic_ai.model_config import MODEL, chat
from pydantic import BaseModel

from agentic_ai.memory.travel_state import TravelState

class StateUpdate(BaseModel):
    destination: str | None = None
    budget: int | None = None
    hotel_preference: str | None = None


class StateExtractor:

    def extract(
        self,
        user_message: str,
        current_state: TravelState
    ) -> StateUpdate:

        response = chat(
            model=MODEL,
            think=False,
            format=StateUpdate.model_json_schema(),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract travel information explicitly updated "
                        "in the latest user message. "
                        "Return null for fields not updated. "
                        "Do not infer missing information. "
                        "Budget must be a numeric amount."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Current state: {current_state.model_dump_json()}\n"
                        f"Latest user message: {user_message}"
                    )
                }
            ]
        )

        return StateUpdate.model_validate_json(
            response.message.content
        )