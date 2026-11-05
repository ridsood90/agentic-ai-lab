import json
from pathlib import Path

cases_file = Path("evals/cases.json")

with cases_file.open("r") as file:
    cases = json.load(file)

print(f"Loaded {len(cases)} cases from {cases_file}")

for case in cases:
    print(
        f"{case['id']} | "
        f"{case['category']} | "
        f"{case['failure_mode']}"
    )
 