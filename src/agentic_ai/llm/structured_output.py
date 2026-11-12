from ollama import chat
from agentic_ai.model_config import MODEL
from pydantic import BaseModel


class FlightSearch(BaseModel):
    origin: str
    destination: str
    max_price: int

def extract_flight_details(prompt: str) -> FlightSearch:
    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format=FlightSearch.model_json_schema()  # Specify the expected output format
    )

    return FlightSearch.model_validate_json(response.message.content)