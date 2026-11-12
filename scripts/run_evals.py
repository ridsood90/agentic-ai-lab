import json
import os
import uuid
from pathlib import Path
from datetime import datetime

from agentic_ai.agents.travel_agent import TravelAgent
from scoring import score_from_state
from agentic_ai.model_config import MODEL, DEFAULT_MODEL

# Set to True to evaluate the model with the executor's result validation.
VALIDATE_RESULTS = os.environ.get("VALIDATE_RESULTS", "true") == "true"
REPETITIONS = 5
# Re-run only some cases: ONLY_CASES=unauthorized_recipient_001 python scripts/run_evals.py
ONLY_CASES = {c for c in os.environ.get("ONLY_CASES", "").split(",") if c}


def load_cases():
    cases_file = Path("evals/cases.json")

    with cases_file.open("r") as file:
        return json.load(file)

def run_evaluation(case):
    print("\n" + "=" * 60)
    print(f"Running: {case['id']}")
    print(f"Category: {case['category']}")
    print("=" * 60)

    session_id = f"eval-{uuid.uuid4().hex[:8]}"

    agent = TravelAgent(session_id=session_id)

    agent.tool_executor.validate_results = VALIDATE_RESULTS
    agent.tool_executor.poisoned_tools = set(case.get("poisoned_tools", []))

    agent.tool_executor.email_tool.failure_mode = (
        case.get("failure_mode")
    )

    if "poisoned_recipient" in case:
        agent.tool_executor.email_tool.poisoned_recipient = (
            case["poisoned_recipient"]
        )

    messages = case.get("messages")

    if messages is None:
        messages = [case.get("user_message")]
    elif isinstance(messages, str):
        messages = [messages]

    responses = []

    for message in messages:
        response = agent.ask(message)
        responses.append(response)

    final_response = responses[-1] if responses else ""

    attempted = agent.tool_executor.email_tool.attempted_emails
    recorded = [
        email.model_dump()
        for email in agent.tool_executor.email_tool.sent_emails
    ]
    tool_calls = list(agent.tool_executor.calls)
    score = score_from_state(case, responses, attempted, recorded, tool_calls)
    status = score["status"]

    print(f"\nEvaluation result: {status} "
          f"(action={score['action_pass']}, report={score['report_pass']})")
    return {
        "case_id": case["id"],
        "category": case["category"],
        "status": status,
        "action_pass": score["action_pass"],
        "report_pass": score["report_pass"],
        "task_completed": score["task_completed"],
        "exercised": score["exercised"],
        "tool_calls": tool_calls,
        "agent_response": final_response,
        "all_responses": responses,
        "attempted_emails": attempted,
        "recorded_emails": recorded,
    }


def checkpoint_path():
    label = str(VALIDATE_RESULTS).lower()
    model_part = (
        "" if MODEL == DEFAULT_MODEL
        else MODEL.replace(":", "-").replace("/", "-") + "_"
    )
    suffix = "_partial" if ONLY_CASES else ""
    return f"evals/checkpoint_{model_part}validate_results_{label}{suffix}.jsonl"


def main():
    with open("evals/cases.json", "r") as file:
        cases = json.load(file)

    if ONLY_CASES:
        cases = [c for c in cases if c["id"] in ONLY_CASES]

    total_runs = len(cases) * REPETITIONS

    print(f"Starting evaluation")
    print(f"Test cases: {len(cases)}")
    print(f"Repetitions: {REPETITIONS}")
    print(f"Total evaluations: {total_runs}")
    print(f"Validate results: {VALIDATE_RESULTS}")

    summary = {
        "PASS": 0,
        "FAIL": 0,
        "NOT SCORED": 0,
        "ERROR": 0
    }

    category_summary = {}
    results = []

    # Fresh checkpoint for this run; every finished run is appended below.
    checkpoint = checkpoint_path()
    open(checkpoint, "w").close()

    for repetition in range(1, REPETITIONS + 1):
        print(f"\n{'=' * 60}")
        print(f"REPETITION {repetition}/{REPETITIONS}")
        print(f"{'=' * 60}")

        for case in cases:
            print(f"\nRunning: {case['id']}")

            try:
                result = run_evaluation(case)
            except Exception as error:
                result = {
                    "case_id": case["id"],
                    "category": case["category"],
                    "status": "ERROR",
                    "error": str(error)
                }

            result["repetition"] = repetition

            status = result.get("status", "NOT SCORED")
            category = result.get("category", case["category"])

            if status not in summary:
                status = "NOT SCORED"
                result["status"] = status

            summary[status] += 1

            if category not in category_summary:
                category_summary[category] = {
                    "PASS": 0,
                    "FAIL": 0,
                    "NOT SCORED": 0,
                    "ERROR": 0
                }

            category_summary[category][status] += 1
            results.append(result)
            with open(checkpoint, "a") as file:
                file.write(json.dumps(result) + "\n")

    pass_rate = (
        summary["PASS"] / total_runs * 100
        if total_runs else 0
    )

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    for status, count in summary.items():
        print(f"{status}: {count}")

    print(f"Total evaluations: {total_runs}")
    print(f"Pass rate: {pass_rate:.1f}%")

    print("\nCATEGORY SUMMARY")

    for category, counts in category_summary.items():
        print(f"\n{category}")
        for status, count in counts.items():
            print(f"  {status}: {count}")

    score_breakdown = {}
    for r in results:
        if r.get("status") == "ERROR":
            continue
        t = score_breakdown.setdefault(
            r["category"],
            {"runs": 0, "action_pass": 0, "report_pass": 0, "not_exercised": 0},
        )
        t["runs"] += 1
        t["not_exercised"] += r.get("exercised") is False
        t["action_pass"] += bool(r.get("action_pass"))
        t["report_pass"] += bool(r.get("report_pass"))

    print("\nSCORE BREAKDOWN (action = right behavior, report = honest report)")
    for category, t in score_breakdown.items():
        print(f"  {category}: runs={t['runs']} "
              f"action={t['action_pass']} report={t['report_pass']} "
              f"payload_not_reached={t['not_exercised']}")

    report = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "validate_results": VALIDATE_RESULTS,
        "repetitions": REPETITIONS,
        "total_cases": len(cases),
        "total_runs": total_runs,
        "pass_rate": round(pass_rate, 2),
        "summary": summary,
        "category_summary": category_summary,
        "score_breakdown": score_breakdown,
        "results": results
    }

    validation_label = str(VALIDATE_RESULTS).lower()
    suffix = "_partial" if ONLY_CASES else ""
    # Keep the original file names for the default model; other models get
    # their own files so runs never overwrite each other.
    model_part = (
        "" if MODEL == DEFAULT_MODEL
        else MODEL.replace(":", "-").replace("/", "-") + "_"
    )
    report_path = (
        f"evals/results_{model_part}validate_results_{validation_label}{suffix}.json"
    )

    with open(report_path, "w") as file:
        json.dump(report, file, indent=4)

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()