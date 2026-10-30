from pydantic import BaseModel
from agentic_ai.tools.tool_executor import ToolExecutor
from agentic_ai.tools.tool_errors import RetryableToolError

class TestInput(BaseModel):
    destination: str

attempt_count = 0

def unstable_flight_tool(destination: str):
    global attempt_count

    attempt_count += 1

    if attempt_count < 3:
        raise RetryableToolError("Temporary network failure")

    return f"Flights found for the {destination}"

executor = ToolExecutor()

executor.tools["unstable_flight_tool"] = (
    unstable_flight_tool,
    TestInput
)

result = executor.execute(
    "unstable_flight_tool",
    {"destination" : "Paris"},
    max_attempts=3,
    retry_delay=0.5
)

print(result)
print("Total attempts: ", attempt_count)