from typing import Any
from pydantic import BaseModel, ValidationError
import time

from agentic_ai.tools.flight_tool import search_flights
from agentic_ai.tools.hotel_tool import search_hotels
from agentic_ai.tools.email_tool import MockEmailTool
from agentic_ai.tools.tool_errors import RetryableToolError

class FlightSearchInput(BaseModel):
    destination: str

class HotelSearchInput(BaseModel):
    city: str

class EmailInput(BaseModel):
    recipient: str
    subject: str
    body: str

class ToolResult(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None

class ToolExecutor:
    def __init__(self):
        self.email_tool = MockEmailTool()
        
        self.tools = {
            "search_flights": (
                search_flights,
                FlightSearchInput
            ),
            "search_hotels": (
                search_hotels,
                HotelSearchInput
            ),
            "send_email": (
                self.email_tool.send_email,
                EmailInput
            )
        }

    def _validate_result(self, name, result, arguments):
        if name == "send_email":
            if not isinstance(result, dict):
                raise ValueError("Invalid email tool response.")

        if result.get("status") != "sent":
            raise ValueError("Email tool did not confirm success.")

        if result.get("recipient") != arguments["recipient"]:
            raise ValueError("Email recipient mismatch.")

        return result

    def execute(
            self, 
            name: str, 
            arguments: dict,
            max_attempts: int = 3,
            retry_delay: float = 1.0
        ) -> ToolResult:

        if name not in self.tools:
            return ToolResult(
                success=False,
                error=f"Unknown Tool: {name}"
            )

        if max_attempts < 1:
            raise ValidationError("max attempts must be atleast 1")

        tool_function, input_model = self.tools[name]

        try:
            validated = input_model.model_validate(arguments)
        except ValidationError as error:
                    return ToolResult(
                        success=False,
                        error=f"Invalid Arguments: {error}"
                    )

        for attempt in range(1, max_attempts + 1):
            try:
                result = tool_function(**validated.model_dump())

                result = self._validate_result(name, result, validated.model_dump())

                return ToolResult(
                    success=True,
                    data=result
                )
        
            except RetryableToolError as error:
                 if attempt == max_attempts:
                    return ToolResult(
                        success=False,
                        error=f"Tool failed after {attempt} attempts: {error}"
                    )
                  
                 print(
                    f"Attempt {attempt} failed. "
                    f"Retrying in {retry_delay} seconds...."
                 )

                 time.sleep(retry_delay)

            except Exception as error:
                 return ToolResult(
                      success= False,
                      error= f"Non-retryable tool failure: {error}"
                 )