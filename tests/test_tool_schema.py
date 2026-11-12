"""The model must only ever see plain tool parameters.

Ollama builds each tool's schema from the Python function signature, so any
test-harness parameter (such as a `poisoned` flag) on search_flights or
search_hotels would be visible to the model and contaminate the eval.
"""
import inspect

from agentic_ai.tools.flight_tool import search_flights
from agentic_ai.tools.hotel_tool import search_hotels


def test_search_tools_expose_only_real_parameters():
    assert list(inspect.signature(search_flights).parameters) == ["destination"]
    assert list(inspect.signature(search_hotels).parameters) == ["city"]


if __name__ == "__main__":
    test_search_tools_expose_only_real_parameters()
    print("ok: model-visible tool schemas are clean")
