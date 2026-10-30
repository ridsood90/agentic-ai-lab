from agentic_ai.tools.tool_executor import ToolExecutor

executor = ToolExecutor()

print("\n TEST 1: Valid flight search")
print(
    executor.execute(
        "search_flights",
        {"destination" : "Paris"}
    )
)

print("\n TEST 2: Missing required argument")
print(
    executor.execute(
        "search_flights",
        {}
    )
)

print("\nTEST 3: Unknown tool")
print(
    executor.execute(
        "search_trains",
        {"destination": "Paris"}
    )
)

print("\nTEST 4: Valid hotel search")
print(
    executor.execute(
        "search_hotels",
        {"city": "Paris"}
    )
)
