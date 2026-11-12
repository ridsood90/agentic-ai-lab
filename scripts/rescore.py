"""Re-score stored results with scripts/scoring.py without re-running the model.

Usage: python scripts/rescore.py evals/results_validate_results_false.json
"""
import json
import sys
from collections import defaultdict

from scoring import score_from_state

cases = {c["id"]: c for c in json.load(open("evals/cases.json"))}

for path in sys.argv[1:]:
    if path.endswith(".jsonl"):
        # Checkpoint from an interrupted run: one result per line.
        data = {"results": [json.loads(line) for line in open(path) if line.strip()]}
    else:
        data = json.load(open(path))
    table = defaultdict(lambda: {"runs": 0, "action": 0, "report": 0, "both": 0, "not_reached": 0})
    flagged = []
    for r in data["results"]:
        if r.get("status") == "ERROR":
            continue
        case = cases[r["case_id"]]
        s = score_from_state(case, r["all_responses"],
                             r["attempted_emails"], r["recorded_emails"],
                             r.get("tool_calls"))
        t = table[r["category"]]
        t["runs"] += 1
        t["action"] += bool(s["action_pass"])
        t["report"] += bool(s["report_pass"])
        t["both"] += s["status"] == "PASS"
        t["not_reached"] += s["exercised"] is False
        if not s["report_pass"] or not s["action_pass"]:
            flagged.append((r["case_id"], s["action_pass"], s["report_pass"],
                            r["agent_response"][:110].replace("\n", " ")))
    print(f"\n== {path} (validate_results={data.get('validate_results')})")
    for cat, t in table.items():
        print(f"{cat:15} runs={t['runs']:3} action={t['action']:3} "
              f"report={t['report']:3} both={t['both']:3} "
              f"payload_not_reached={t['not_reached']}")
    for f in flagged:
        print("  FLAG", f)
