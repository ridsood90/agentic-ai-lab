from ollama import chat
from pydantic import BaseModel


class FlightSearch(BaseModel):
    origin: str
    destination: str
    max_price: int

def extract_flight_details(prompt: str) -> FlightSearch:
    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format=FlightSearch.model_json_schema()  # Specify the expected output format
    )

    return FlightSearch.model_validate_json(response.message.content)