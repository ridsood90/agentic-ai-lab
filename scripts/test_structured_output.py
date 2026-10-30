from agentic_ai.llm.structured_output import extract_flight_details

result = extract_flight_details("Find me a flight from Amsterdam to New York under 300 euros.")

print(result)
print("Destination: ", result.destination)
print("Max Price: ", result.max_price)